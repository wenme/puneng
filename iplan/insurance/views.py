# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from models import product, premium_rate, insurer, life, ci, saving, rule
from common import generate_response, return_code
import datetime
import json
import MySQLdb

def median(arr):
    if not arr:
        return 0
    arr = sorted(arr)
    len_arr = len(arr)
    if len_arr % 2 == 1:
        return arr[len_arr/2]
    else:
        return float((arr[len_arr/2-1]+arr[len_arr/2])) / 2.0


def expected_saving(expected_irr, yearly_mortage, year_of_mortage, years):
    total_saving = yearly_mortage
    for i in range(0, years):
        if i < year_of_mortage-1:
            total_saving = total_saving * (1 + expected_irr) + yearly_mortage
        else:
            total_saving = total_saving * (1 + expected_irr)
    return total_saving


# check insurer's region first
def get_premium(request):
    if request.method == 'POST':
        # print request.POST
        product_type = request.POST.get('product_type', None)
        sum_insured = request.POST.get('sum_insured', None)
        gender = request.POST.get('gender', None)
        application_age = request.POST.get('application_age', None)
        premium_period = request.POST.get('premium_period', None)
        ip_addr = request.POST.get('ip_addr', None)
        session_id = request.POST.get('session_id', None)
        client_tag = str(ip_addr) + '_' + str(session_id)
        benefit_age_max = 100

        if product_type == None or sum_insured == None or gender == None or application_age == None or premium_period == None:
            errmsg = 'params error'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.PARAM_ERROR, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

        try:
            # get CN premium
            product_code_arr = []
            for insurer_obj in insurer.objects.filter(region='CN'):
                for product_obj in product.objects.filter(product_type=int(product_type), insurer_code=insurer_obj.insurer_code, saving=1):
                    product_code_arr.append(product_obj.product_code)
            premium_arr = []
            for p_code in product_code_arr:
                premium_rate_obj_arr = premium_rate.objects.filter(product_code=p_code, application_age=application_age, gender=gender, premium_period=premium_period, benefit_age_max=benefit_age_max)
                if len(premium_rate_obj_arr) != 0:
                    premium_arr.append(float(premium_rate_obj_arr[0].annual_premium_10k))
                    print premium_rate_obj_arr[0].product_code, premium_rate_obj_arr[0].annual_premium_10k
            cn_premium = median(premium_arr) * float(sum_insured) / 10000.0

            print '='*10
            # get HK premium
            product_code_arr = []
            for insurer_obj in insurer.objects.filter(region='HK'):
                for product_obj in product.objects.filter(product_type=int(product_type), insurer_code=insurer_obj.insurer_code, saving=1):
                    product_code_arr.append(product_obj.product_code)
            premium_arr = []
            for p_code in product_code_arr:
                premium_rate_obj_arr = premium_rate.objects.filter(product_code=p_code, application_age=application_age, gender=gender, premium_period=premium_period, benefit_age_max=benefit_age_max)
                if len(premium_rate_obj_arr) != 0:
                    premium_arr.append(float(premium_rate_obj_arr[0].annual_premium_10k))
                    print premium_rate_obj_arr[0].product_code, premium_rate_obj_arr[0].annual_premium_10k
            hk_premium = median(premium_arr) * float(sum_insured) / 10000.0

            # discount
            discount = float(hk_premium / cn_premium)
            premium_info_json = {}
            premium_info_json['cn_premium'] = cn_premium
            premium_info_json['hk_premium'] = hk_premium
            premium_info_json['discount'] = discount
            rslt_json = json.dumps(generate_response.gen('premium_info', premium_info_json, return_code.NORMAL_RESPONSE, None))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response
        except Excetion, e:
            errmsg = 'invalid request'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.INVALID_REQUEST, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

def get_premium_rate_range(request):
    if request.method == 'POST':
        product_code = request.POST.get('product_code', None)
        application_age = request.POST.get('application_age', None)
        if product_code == None:
            errmsg = 'params error'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.PARAM_ERROR, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

        try:
            premium_rate_range_json = {}
            application_age_min = 100
            application_age_max = 0
            premium_period_range = []
            benefit_age_range = []
            premium_rate_obj_arr = []
            if application_age == None:
                premium_rate_obj_arr = premium_rate.objects.filter(product_code=int(product_code))
            else:
                premium_rate_obj_arr = premium_rate.objects.filter(product_code=int(product_code), application_age=int(application_age))
            for premium_rate_obj in premium_rate_obj_arr:
                if premium_rate_obj.application_age < application_age_min:
                    application_age_min = premium_rate_obj.application_age
                if premium_rate_obj.application_age > application_age_max:
                    application_age_max = premium_rate_obj.application_age
                premium_period_range.append(premium_rate_obj.premium_period)
                benefit_age_range.append(premium_rate_obj.benefit_age_max)
            premium_rate_range_json['premium_period_range'] = list(set(premium_period_range))
            premium_rate_range_json['benefit_age_range'] = list(set(benefit_age_range))
            premium_rate_range_json['application_age_min'] = application_age_min
            premium_rate_range_json['application_age_max'] = application_age_max
            
            rslt_json = json.dumps(generate_response.gen('premium_rate_range', premium_rate_range_json, return_code.NORMAL_RESPONSE, None))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response
        except Excetion, e:
            errmsg = 'invalid request'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.INVALID_REQUEST, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

def get_premium_rate(request):
    if request.method == 'POST':
        product_code = request.POST.get('product_code', None)
        application_age = request.POST.get('application_age', None)
        gender = request.POST.get('gender', None)
        smoker = request.POST.get('smoker', None)
        premium_period = request.POST.get('premium_period', None)
        benefit_age_max = request.POST.get('benefit_age_max', 100)
        sum_insured = request.POST.get('sum_insured', 0)
        if product_code == None or application_age == None or gender == None or smoker == None or premium_period == None:
            errmsg = 'params error'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.PARAM_ERROR, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

        try:
            premium_rate_obj = premium_rate.objects.filter(product_code=int(product_code), application_age=int(application_age), gender__in=[int(gender), 2], smoker__in=[int(smoker), 2], premium_period=int(premium_period), benefit_age_max=int(benefit_age_max))
            premium_rslt = -1
            if len(premium_rate_obj) > 0:
                premium_rslt = premium_rate_obj[0].annual_premium_10k * float(sum_insured)
            rslt = {}
            rslt['premium'] = premium_rslt
            rslt['feature'] = product.objects.filter(product_code=int(product_code))[0].feature_desc
            rslt_json = json.dumps(generate_response.gen('premium_info', rslt, return_code.NORMAL_RESPONSE, None))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response
        except Excetion, e:
            errmsg = 'invalid request'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.INVALID_REQUEST, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

def product_compare(request):
    if request.method == 'POST':
        product_code_a = request.POST.get('product_a', None)
        product_code_b = request.POST.get('product_b', None)
        ip_addr = request.POST.get('ip_addr', None)
        session_id = request.POST.get('session_id', None)
        client_tag = str(ip_addr) + '_' + str(session_id)

        if product_code_a == None or product_code_b == None:
            errmsg = 'params error'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.PARAM_ERROR, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

        try:
            # product a info
            product_a_json = {}
            product_a = product.objects.filter(product_code=int(product_code_a))[0]
            insurer_a = insurer.objects.filter(insurer_code=product_a.insurer_code)[0]
            product_a_json['product_code'] = product_a.product_code
            product_a_json['product_name'] = product_a.product_name
            product_a_json['insurer_name'] = insurer_a.insurer_name
            product_a_json['insurer_logo'] = insurer_a.logo
            product_a_json['application_age'] = [product_a.application_age_min, product_a.application_age_max]
            product_a_json['benefit_age_max'] = product_a.benefit_age_max
            product_a_json['terms'] = product_a.terms
            product_a_json['brochure'] = product_a.brochure

            life_info = product_a.life
            product_a_life_json = {}
            if life_info == 1:
                death_illness = ''
                death_accident = ''
                life_product_obj_arr = life.objects.filter(product_code=int(product_code_a))
                death_illness = '保额X' if life_product_obj_arr[0].claim_base==1 else '保费X'
                death_accident = '保额X' if life_product_obj_arr[0].claim_base==1 else '保费X'
                death_illness += str( int(life_product_obj_arr[0].death_illness*100) ) + '%'
                death_accident += str( int(life_product_obj_arr[0].death_accident*100) ) + '%'
                saving_product_obj_arr = saving.objects.filter(product_code=int(product_code_a))
                # if len(saving_product_obj_arr) > 0:
                #     if saving_product_obj_arr[0].par != 0:
                #         death_illness += ' + 分红'
                #         death_accident += ' + 分红'
                product_a_life_json['death_illness'] = death_illness
                product_a_life_json['death_accident'] = death_accident
                claim_18 = life_product_obj_arr[0].claim_18
                if claim_18 == 0:
                    claim_18_str = '无限制'
                elif claim_18 == 1:
                    claim_18_str = '不超过10万'
                else:
                    claim_18_str = '退还保费'
                product_a_life_json['claim_18'] = claim_18_str
                advance_payment_with_ci = life_product_obj_arr[0].advance_payment_with_ci
                if advance_payment_with_ci == 0:
                    advance_payment_with_ci_str = '不共用保额'
                else:
                    advance_payment_with_ci_str = '共用保额'
                product_a_life_json['advance_payment_with_ci'] = advance_payment_with_ci_str
                product_a_life_json['waiting_period'] = life_product_obj_arr[0].waiting_period
                product_a_life_json['permanent_disability'] = '保障' if life_product_obj_arr[0].permanent_disability else '不保障'
            product_a_json['life'] = product_a_life_json

            ci_info = product_a.ci
            product_a_ci_json = {}
            if ci_info == 1:
                ci_product_obj_arr = ci.objects.filter(product_code=int(product_code_a))
                product_a_ci_json['ci'] = ci_product_obj_arr[0].ci
                product_a_ci_json['early_stage_ci'] = ci_product_obj_arr[0].early_stage_ci
                product_a_ci_json['non_ci'] = ci_product_obj_arr[0].non_ci
                product_a_ci_json['juvenile_minor_illness'] = ci_product_obj_arr[0].juvenile_minor_illness
                product_a_ci_json['ci_max_claim'] = ci_product_obj_arr[0].ci_max_claim
                product_a_ci_json['face_amount_growth_rate'] = ci_product_obj_arr[0].face_amount_growth_rate * 100
                product_a_ci_json['waiting_period'] = ci_product_obj_arr[0].waiting_period
                product_a_ci_json['early_stage_ci_claim'] = ci_product_obj_arr[0].early_stage_ci_claim * 100
            product_a_json['ci'] = product_a_ci_json

            saving_info = product_a.saving
            product_a_saving_json = {}
            if saving_info == 1:
                saving_product_obj_arr = saving.objects.filter(product_code=int(product_code_a))
                product_a_saving_json['y30_expected_irr'] = saving_product_obj_arr[0].y30_expected_irr * 100
                product_a_saving_json['y30_guaranteed_irr'] = saving_product_obj_arr[0].y30_guaranteed_irr * 100
                product_a_saving_json['surrender_partially_year'] = '不能' if saving_product_obj_arr[0].surrender_partially_year==0 else '可以'
                y20_irr = saving_product_obj_arr[0].y20_expected_irr
                product_a_saving_json['y20_total_saving'] = expected_saving(y20_irr, 100000, 10, 20)
                y30_irr = saving_product_obj_arr[0].y30_expected_irr
                product_a_saving_json['y30_total_saving'] = expected_saving(y30_irr, 100000, 10, 30)
                y40_irr = saving_product_obj_arr[0].y40_expected_irr
                product_a_saving_json['y40_total_saving'] = expected_saving(y40_irr, 100000, 10, 40)
                # product_a_saving_json['expected_irr_avg'] = saving_product_obj_arr[0].expected_irr_avg * 100
                # product_a_saving_json['guaranteed_irr'] = saving_product_obj_arr[0].guaranteed_irr * 100
                # product_a_saving_json['par_distribution'] = saving_product_obj_arr[0].par_distribution * 100
                # currency_type = str(product_a.currency)
                # y20_irr = saving_product_obj_arr[0].y20_expected_irr
                # y30_irr = saving_product_obj_arr[0].y30_expected_irr
                # y40_irr = saving_product_obj_arr[0].y40_expected_irr
                # product_a_saving_json['total_mortage'] = '200000' + ' ' + currency_type
                # product_a_saving_json['total_saving_20'] = str(expected_saving(y20_irr, 10000, 20, 20)) + ' ' + currency_type
                # product_a_saving_json['total_saving_30'] = str(expected_saving(y30_irr, 10000, 20, 30)) + ' ' + currency_type
                # product_a_saving_json['total_saving_40'] = str(expected_saving(y40_irr, 10000, 20, 40)) + ' ' + currency_type
            product_a_json['saving'] = product_a_saving_json

            # product b info
            product_b_json = {}
            product_b = product.objects.filter(product_code=int(product_code_b))[0]
            insurer_b = insurer.objects.filter(insurer_code=product_b.insurer_code)[0]
            product_b_json['product_code'] = product_b.product_code
            product_b_json['product_name'] = product_b.product_name
            product_b_json['insurer_name'] = insurer_b.insurer_name
            product_b_json['insurer_logo'] = insurer_b.logo
            product_b_json['application_age'] = [product_b.application_age_min, product_b.application_age_max]
            product_b_json['benefit_age_max'] = product_b.benefit_age_max
            product_b_json['terms'] = product_b.terms
            product_b_json['brochure'] = product_b.brochure

            life_info = product_b.life
            product_b_life_json = {}
            if life_info == 1:
                death_illness = ''
                death_accident = ''
                life_product_obj_arr = life.objects.filter(product_code=int(product_code_b))
                death_illness = '保额X' if life_product_obj_arr[0].claim_base==1 else '保费X'
                death_accident = '保额X' if life_product_obj_arr[0].claim_base==1 else '保费X'
                death_illness += str( int(life_product_obj_arr[0].death_illness*100) ) + '%'
                death_accident += str( int(life_product_obj_arr[0].death_accident*100) ) + '%'
                saving_product_obj_arr = saving.objects.filter(product_code=int(product_code_b))
                # if len(saving_product_obj_arr) > 0:
                #     if saving_product_obj_arr[0].par != 0:
                #         death_illness += ' + 分红'
                #         death_accident += ' + 分红'
                product_b_life_json['death_illness'] = death_illness
                product_b_life_json['death_accident'] = death_accident
                claim_18 = life_product_obj_arr[0].claim_18
                if claim_18 == 0:
                    claim_18_str = '无限制'
                elif claim_18 == 1:
                    claim_18_str = '不超过10万'
                else:
                    claim_18_str = '退还保费'
                product_b_life_json['claim_18'] = claim_18_str
                advance_payment_with_ci = life_product_obj_arr[0].advance_payment_with_ci
                if advance_payment_with_ci == 0:
                    advance_payment_with_ci_str = '不共用保额'
                else:
                    advance_payment_with_ci_str = '共用保额'
                product_b_life_json['advance_payment_with_ci'] = advance_payment_with_ci_str
                product_b_life_json['waiting_period'] = life_product_obj_arr[0].waiting_period
                product_b_life_json['permanent_disability'] = '保障' if life_product_obj_arr[0].permanent_disability else '不保障'
            product_b_json['life'] = product_b_life_json

            ci_info = product_b.ci
            product_b_ci_json = {}
            if ci_info == 1:
                ci_product_obj_arr = ci.objects.filter(product_code=int(product_code_b))
                product_b_ci_json['ci'] = ci_product_obj_arr[0].ci
                product_b_ci_json['early_stage_ci'] = ci_product_obj_arr[0].early_stage_ci
                product_b_ci_json['non_ci'] = ci_product_obj_arr[0].non_ci
                product_b_ci_json['juvenile_minor_illness'] = ci_product_obj_arr[0].juvenile_minor_illness
                product_b_ci_json['ci_max_claim'] = ci_product_obj_arr[0].ci_max_claim
                product_b_ci_json['face_amount_growth_rate'] = ci_product_obj_arr[0].face_amount_growth_rate * 100
                product_b_ci_json['waiting_period'] = ci_product_obj_arr[0].waiting_period
                product_b_ci_json['early_stage_ci_claim'] = ci_product_obj_arr[0].early_stage_ci_claim * 100
            product_b_json['ci'] = product_b_ci_json

            saving_info = product_b.saving
            product_b_saving_json = {}
            if saving_info == 1:
                saving_product_obj_arr = saving.objects.filter(product_code=int(product_code_b))
                product_b_saving_json['y30_expected_irr'] = saving_product_obj_arr[0].y30_expected_irr * 100
                product_b_saving_json['y30_guaranteed_irr'] = saving_product_obj_arr[0].y30_guaranteed_irr * 100
                product_b_saving_json['surrender_partially_year'] = '不能' if saving_product_obj_arr[0].surrender_partially_year==0 else '可以'
                y20_irr = saving_product_obj_arr[0].y20_expected_irr
                product_b_saving_json['y20_total_saving'] = expected_saving(y20_irr, 100000, 10, 20)
                y30_irr = saving_product_obj_arr[0].y30_expected_irr
                product_b_saving_json['y30_total_saving'] = expected_saving(y30_irr, 100000, 10, 30)
                y40_irr = saving_product_obj_arr[0].y40_expected_irr
                product_b_saving_json['y40_total_saving'] = expected_saving(y40_irr, 100000, 10, 40)
                # saving_product_obj_arr = saving.objects.filter(product_code=int(product_code_b))
                # product_b_saving_json['expected_irr_avg'] = saving_product_obj_arr[0].expected_irr_avg * 100
                # product_b_saving_json['guaranteed_irr'] = saving_product_obj_arr[0].guaranteed_irr * 100
                # product_b_saving_json['par_distribution'] = saving_product_obj_arr[0].par_distribution * 100
                # currency_type = str(product_b.currency)
                # y20_irr = saving_product_obj_arr[0].y20_expected_irr
                # y30_irr = saving_product_obj_arr[0].y30_expected_irr
                # y40_irr = saving_product_obj_arr[0].y40_expected_irr
                # product_b_saving_json['total_mortage'] = '200000' + ' ' + currency_type
                # product_b_saving_json['total_saving_20'] = str(expected_saving(y20_irr, 10000, 20, 20)) + ' ' + currency_type
                # product_b_saving_json['total_saving_30'] = str(expected_saving(y30_irr, 10000, 20, 30)) + ' ' + currency_type
                # product_b_saving_json['total_saving_40'] = str(expected_saving(y40_irr, 10000, 20, 40)) + ' ' + currency_type
            product_b_json['saving'] = product_b_saving_json
            
            product_cmp_json = {}
            product_cmp_json['product_a'] = product_a_json
            product_cmp_json['product_b'] = product_b_json
            rslt_json = json.dumps(generate_response.gen('product_cmp', product_cmp_json, return_code.NORMAL_RESPONSE, None))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response
        except Excetion, e:
            errmsg = 'invalid request'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.INVALID_REQUEST, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

def get_insurance_need(request):
    if request.method == 'POST':
        ans1 = request.POST.get('ans1', None)
        ans2 = request.POST.get('ans2', None)
        ans3 = request.POST.get('ans3', None)
        ans4 = request.POST.get('ans4', None)
        ans5 = request.POST.get('ans5', None)
        ans6 = request.POST.get('ans6', None)
        ans7 = request.POST.get('ans7', None)
        ans8 = request.POST.get('ans8', None)
        ip_addr = request.POST.get('ip_addr', None)
        session_id = request.POST.get('session_id', None)
        client_tag = str(ip_addr) + '_' + str(session_id)

        if ans1 == None or ans2 == None or ans3 == None or ans4 == None or ans5 == None or ans6 == None or ans7 == None or ans8 == None:
            errmsg = 'params error'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.PARAM_ERROR, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response

        try:
            # Life insurance
            family_liability = int(ans3)*10000 + int(ans4) * 5 * 10000
            non_social_security_L = 0
            gov_medical_care_L = 0
            smoker_L = 0
            hereditary_disease_L = 0
            traveller_L = 0

            # critical_illness insurance
            non_social_security_CI = 0
            gov_medical_care_CI = 0
            smoker_CI = 0
            hereditary_disease_CI = 0
            traveller_CI = 0

            # hospital insurance
            non_social_security_HE = 0
            gov_medical_care_HE = 0
            smoker_HE = 0
            hereditary_disease_HE = 0
            traveller_HE = 0

            # accidental protection insurance
            non_social_security_AP = 0
            gov_medical_care_AP = 0
            smoker_AP = 0
            hereditary_disease_AP = 0
            traveller_AP = 0

            # accidental medical insurance
            non_social_security_AME = 0
            gov_medical_care_AME = 0
            smoker_AME = 0
            hereditary_disease_AME = 0
            traveller_AME = 0

            # set values according to the answers
            rule_obj_arr = rule.objects.all()
            social_security = int(ans1)
            inheritance = int(ans6)
            trip_frequency = int(ans7)
            smoking = int(ans5)
            if social_security == 3:
                print 'non social'
                non_social_security_L = rule_obj_arr[0].non_social_security
                non_social_security_CI = rule_obj_arr[1].non_social_security
                non_social_security_HE = rule_obj_arr[2].non_social_security
                non_social_security_AP = rule_obj_arr[3].non_social_security
                non_social_security_AME = rule_obj_arr[4].non_social_security
            if social_security == 2:
                print 'gov social'
                gov_medical_care_L = rule_obj_arr[0].gov_medical_care
                gov_medical_care_CI = rule_obj_arr[1].gov_medical_care
                gov_medical_care_HE = rule_obj_arr[2].gov_medical_care
                gov_medical_care_AP = rule_obj_arr[3].gov_medical_care
                gov_medical_care_AME = rule_obj_arr[4].gov_medical_care
            if smoking == 1:
                print 'smoke'
                smoker_L = rule_obj_arr[0].smoker
                smoker_CI = rule_obj_arr[1].smoker
                smoker_HE = rule_obj_arr[2].smoker
                smoker_AP = rule_obj_arr[3].smoker
                smoker_AME = rule_obj_arr[4].smoker
            if inheritance == 1:
                print 'inheritance'
                hereditary_disease_L = rule_obj_arr[0].hereditary_disease
                hereditary_disease_CI = rule_obj_arr[1].hereditary_disease
                hereditary_disease_HE = rule_obj_arr[2].hereditary_disease
                hereditary_disease_AP = rule_obj_arr[3].hereditary_disease
                hereditary_disease_AME = rule_obj_arr[4].hereditary_disease
            if trip_frequency == 1:
                print 'traveller'
                traveller_L = rule_obj_arr[0].traveller
                traveller_CI = rule_obj_arr[1].traveller
                traveller_HE = rule_obj_arr[2].traveller
                traveller_AP = rule_obj_arr[3].traveller
                traveller_AME = rule_obj_arr[4].traveller

            # fill out need
            life_need = rule_obj_arr[0].benchmark + float(ans2) * float(family_liability) + non_social_security_L + gov_medical_care_L + smoker_L + hereditary_disease_L + traveller_L
            critical_illness_need1 = rule_obj_arr[1].benchmark + non_social_security_CI + gov_medical_care_CI + smoker_CI + hereditary_disease_CI + traveller_CI
            critical_illness_need2 = int(ans8) * 10000 * 5 if int(ans8)<30 else int(ans8) * 10000 * 3
            critical_illness_need = max(critical_illness_need1, critical_illness_need2)
            hospital_expense_need = rule_obj_arr[2].benchmark + non_social_security_HE + gov_medical_care_HE + smoker_HE + hereditary_disease_HE + traveller_HE
            accidental_protection_need = rule_obj_arr[3].benchmark + non_social_security_AP + gov_medical_care_AP + smoker_AP + hereditary_disease_AP + traveller_AP
            accidental_medical_expense_need = rule_obj_arr[4].benchmark + non_social_security_AME + gov_medical_care_AME + smoker_AME + hereditary_disease_AME + traveller_AME

            insurance_need_json = {}
            insurance_need_json['life_need'] = life_need / 10000
            insurance_need_json['critical_illness_need'] = critical_illness_need / 10000
            insurance_need_json['hospital_expense_need'] = hospital_expense_need / 10000
            insurance_need_json['accidental_protection_need'] = accidental_protection_need / 10000
            insurance_need_json['accidental_medical_expense_need'] = accidental_medical_expense_need / 10000

            # product recommendation of PU NENG
            recommend_product_list = []
            recommend_product_code_list = [61,24,21]
            if life_need - critical_illness_need > 30:
                recommend_product_code_list = [61,24,21,133,27]
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
            insurance_need_json['recommend_product_list'] = recommend_product_list
            # end of product recommendation of PU NENG

            rslt_json = json.dumps(generate_response.gen('insurance_need', insurance_need_json, return_code.NORMAL_RESPONSE, None))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response
        except Excetion, e:
            errmsg = 'invalid request'
            rslt_json = json.dumps(generate_response.gen('response', {}, return_code.INVALID_REQUEST, errmsg))
            response = HttpResponse(rslt_json, content_type='application/json')
            response['Content-Length'] = len(rslt_json)
            return response
