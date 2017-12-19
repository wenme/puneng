# -*- coding: utf-8 -*-
from django.shortcuts import render
import json, math
from django.http import HttpResponse
from models import city_salary
from common import generate_response, return_code
from insurance.models import product, insurer

def total_cost_with_inflation(total_cost, year_to_come, expected_inflation):
    return int( float(total_cost) * (float(1+expected_inflation)**year_to_come) )

def monthly_saving(targer_saving, year_to_come, expected_return_rate):
    return int( float(targer_saving) * expected_return_rate / ((1+expected_return_rate)**year_to_come - 1) / 12 )

def retire_fee(request):
    if request.method == 'POST':
#        birthday = request.GET.get('birthday', None)
        gender = request.POST.get('gender', None)
        salary_base = request.POST.get('salary_base', None)
        try:
            city_name = request.POST.get('city', None)
            # print '1', city_name
            city_name = city_name.encode('utf-8')
            # print '2', city_name
        except Exception as e:
            print e
            pass
        expected_retire_age = request.POST.get('expected_retire_age', None)
        expected_monthly_expense = request.POST.get('expected_monthly_expense', None)
        expected_yearly_tourfee = request.POST.get('expected_yearly_tourfee', None)
        expected_yearly_healthcare = request.POST.get('expected_yearly_healthcare', None)
        expected_legacy = request.POST.get('expected_legacy', None)
        age = request.POST.get('age', None)
        expected_inflation = request.POST.get('expected_inflation', 0)
        expected_return_rate = request.POST.get('expected_return_rate', 0)
        expected_inflation = float(expected_inflation) / 100.0
        expected_return_rate = float(expected_return_rate) / 100.0       
        
        #gender: 0 for female, 1 for male
        if gender == '1':
            retire_age_std = 65
            social_security_std = 35
            global_age_avg = 78
        else:
            retire_age_std = 60
            social_security_std = 30
            global_age_avg = 82

        expected_social_security = float(social_security_std - retire_age_std + int(expected_retire_age))
        if expected_social_security < 15:
            # ss for social security
            ss_time_ratio = 0
        else:
            ss_time_ratio = expected_social_security / float(social_security_std)

        city_salary_info = city_salary.objects.filter(city=city_name).order_by('-update_date')[:1]
        if len(city_salary_info) == 0:
            print 'no city found'
        ss_fee_ratio = float(salary_base) / city_salary_info[0].employee_avg_salary
        if ss_fee_ratio < 0.6:
            ss_fee_ratio = 0.6
        if ss_fee_ratio > 3:
            ss_fee_ratio = 3
        expected_monthly_retire_fee = city_salary_info[0].retiree_avg_salary * ss_fee_ratio * ss_time_ratio

        monthly_total_expense = float(expected_monthly_expense) + float(expected_yearly_tourfee) / 12 + float(expected_yearly_healthcare) / 12
#       print expected_retire_age, expected_legacy
        expected_total_expense = monthly_total_expense * 12 * (global_age_avg - float(expected_retire_age)) + float(expected_legacy)

        retire_gap = expected_total_expense - expected_monthly_retire_fee * 12 * (global_age_avg - float(retire_age_std))

        # product recommendation of PU NENG
        recommend_product_list = []
        recommend_product_code_list = [134,31,34]
        for product_obj in product.objects.filter(product_code__in=recommend_product_code_list):
            product_info_tmp = {}
            product_info_tmp['product_code'] = product_obj.product_code
            insurer_code_tmp = product_obj.insurer_code
            product_info_tmp['insurer_code'] = insurer_code_tmp
            product_info_tmp['insurer_logo'] = insurer.objects.filter(insurer_code=insurer_code_tmp)[0].logo
            product_info_tmp['product_name'] = product_obj.product_name
            product_info_tmp['application_age_min'] = product_obj.application_age_min
            product_info_tmp['application_age_max'] = product_obj.application_age_max
            product_info_tmp['benefit_age_max'] = product_obj.benefit_age_max if product_obj.benefit_age_max < 100 else '终身'
            product_type_tmp = product_obj.product_type
            if product_type_tmp == 2:
                product_info_tmp['product_type'] = '重疾险'
            if product_type_tmp == 4:
                product_info_tmp['product_type'] = '人寿险'
            insurer_code_tmp = product_obj.insurer_code
            insurer_obj_tmp = insurer.objects.get(insurer_code=insurer_code_tmp)
            product_info_tmp['insurer_name'] = insurer_obj_tmp.insurer_name
            recommend_product_list.append(product_info_tmp)
        # end of product recommendation of PU NENG

        year_to_come = int(expected_retire_age) - int(age)
        target_saving = total_cost_with_inflation(retire_gap, year_to_come, float(expected_inflation))
        saving_per_month = monthly_saving(target_saving, year_to_come, float(expected_return_rate))
        retirement_fee_json = {
            'expected_monthly_retire_fee': expected_monthly_retire_fee,
            'retire_gap': retire_gap,
            'monthly_total_expense': monthly_total_expense,
            'recommend_product_list': recommend_product_list,
            'monthly_saving': saving_per_month
        }
        rslt_json = json.dumps(generate_response.gen('retirement_fee', retirement_fee_json, return_code.NORMAL_RESPONSE, None))
        response = HttpResponse(rslt_json, content_type='application/json')
        response['Content-Length'] = len(rslt_json)
        return response
