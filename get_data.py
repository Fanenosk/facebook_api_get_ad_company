from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adreportrun import AdReportRun
from facebook_business.adobjects.adsinsights import AdsInsights
#from facebookads.objects import AdUser
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business import adobjects
import mysql.connector
from matplotlib import pyplot as plt
from pandas import DataFrame
import time

my_access_token = ''
my_app_id = ''
my_app_secret = ''
FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

me = AdUser(fbid='me')
my_accounts = list(me.get_ad_accounts())
print(my_accounts)

my_account = my_accounts[0]
campaigns = my_account.get_campaigns()
print(campaigns)

my_account.api_get(fields=[AdAccount.Field.amount_spent])
print(int(my_account[AdAccount.Field.amount_spent])/100)

fields = [
    AdsInsights.Field.campaign_id,
    AdsInsights.Field.clicks,
    AdsInsights.Field.spend,
    AdsInsights.Field.impressions]

count = 0

def wait_for_async_job(async_job):
    global count
    async_job = async_job.api_get()
    while async_job[AdReportRun.Field.async_status] != 'Job Completed' or async_job[
        AdReportRun.Field.async_percent_completion] < 100:
        time.sleep(2)
        async_job = async_job.api_get()
    else:
        print("Job " + str(count) + " completed")
        count += 1
    return async_job.get_result(params={"limit": 1000})

def get_insights(account, date_preset='last_3d'):
    account = AdAccount(account["id"])
    i_async_job = account.get_insights(
        params={
            'level': 'ad',
            'date_preset': date_preset,
            'time_increment': 1},
            fields=fields,
            is_async=True)
    results = [dict(item) for item in wait_for_async_job(i_async_job)]
    return results

elem_insights = []
insights_lists = []
date_preset = 'last_year'
for elem in my_accounts:
            elem_insights = get_insights(elem, date_preset)
            insights_lists.append(elem_insights)

insight_campaign_id_list = []
insight_clicks_list = []
insight_spend_list = []
insight_impressions_list = []
insight_date_start_list = []
insight_date_stop_list = []
for elem1 in insights_lists:
    for elem2 in elem1:
        insight_campaign_id_list.append(int(elem2['campaign_id']))
        insight_clicks_list.append(int(elem2['clicks']))
        insight_spend_list.append(float(elem2['spend']))
        insight_impressions_list.append(int(elem2['impressions']))
        insight_date_start_list.append(elem2['date_start'])
        insight_date_stop_list.append(elem2['date_stop'])

df = DataFrame()
df['campaign_id'] = insight_campaign_id_list
df['clicks'] = insight_clicks_list
df['spend'] = insight_spend_list
df['impressions'] = insight_impressions_list
df['date_start'] = insight_date_start_list
df['date_stop'] = insight_date_stop_list

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="facebook_insights"
)

mycursor = mydb.cursor()

insert_sql = "INSERT into ad_company (campaign_id, clicks, spend, impressions, date_start, date_stop) VALUES (%s, %s, %s, %s, %(to_date)s, %(to_date)s)"

mycursor.execute(insert_sql, df)