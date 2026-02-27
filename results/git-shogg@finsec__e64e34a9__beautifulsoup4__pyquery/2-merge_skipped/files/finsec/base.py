import requests
from pyquery import PyQuery as pq
from datetime import datetime
import pandas as pd
import pdb
import os
import time
from io import StringIO

_BASE_URL_ = 'https://www.sec.gov'
_13F_SEARCH_URL_ = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=13F-HR&count=100'
_REQ_HEADERS_ = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'HOST': 'www.sec.gov',
                }

class FilingBase():
    def __init__(self, cik, declared_user=None):
        if declared_user is not None:
            _REQ_HEADERS_["User-Agent"] = declared_user+";"+_REQ_HEADERS_["User-Agent"]
        self.cik = self._validate_cik(cik)
        self.manager = None
        self._13f_filings = None
        self._13f_amendment_filings = None
        
        self.filings = {}

    def _validate_cik(self, cik:str):
        """Check if CIK is 10 digit string."""
        if not (isinstance(cik, str) and len(cik) == 10 and cik.isdigit()):
            raise Exception("""Invalid CIK Provided""")
        return cik

    def _get_last_100_13f_filings_url(self):
        """Searches the last 13F-HR and 13F-HR/A filings. Returns a 13f_filings variable and 13f_amendment_filings variable"""
        if self._13f_filings is not None or self._13f_amendment_filings is not None:
            return

        webpage = requests.get(_13F_SEARCH_URL_.format(self.cik), headers=_REQ_HEADERS_)
        doc = pq(webpage.text)
        results_table = doc('table[summary="Results"]')
        results_table_df = pd.read_html(StringIO(str(results_table)))[0]
        
        url_endings = []
        url_link_col = results_table_df.columns.get_loc("Format")
        for row in results_table('tr').items():
            tds = row('td')
            try:
                url_endings.append(tds.eq(url_link_col)('a').attr('href'))
            except:
                pass
        results_table_df['url'] = url_endings
        self._13f_filings = results_table_df[results_table_df['Filings'] == "13F-HR"].reset_index(drop=True)
        self._13f_amendment_filings = results_table_df[results_table_df['Filings'] == "13F-HR/A"].reset_index(drop=True)

        return self._13f_filings, self._13f_amendment_filings
    
    def _13f_amendment_filings_period_of_filings(self):
        """This function finds the actual 'period of report' for the 13f amendment filings (this function needs to open the filing url for each and every 13f amendment identified). This is required to understand which particular report is being amended."""
        def _pandas_apply_func(x):
            webpage = requests.get(_BASE_URL_ + x['url'], headers=_REQ_HEADERS_)
            doc = pq(webpage.text)
            period_of_report_div = doc('div:contains("Period of Report")')
            period_of_report_date = period_of_report_div.next('.info').text()
            datetime_obj = datetime.strptime(period_of_report_date, '%Y-%m-%d')
            release_qtr = datetime_obj.month // 3
            year = datetime_obj.year
            time.sleep(0.2)
            return pd.Series([period_of_report_date, "Q{}-{}".format(release_qtr, year)]) 
        self._13f_amendment_filings[['Period of Report', 'Period of Report Quarter Year']] = self._13f_amendment_filings.apply(_pandas_apply_func, axis=1)
        return self._13f_amendment_filings       

    def _get_bs4_text(self, pq_obj):
        try:
            return pq_obj.text()
        except:
            return "N/A"

    def _parse_13f_url(self, url:str, date:str):
        response = requests.get(_BASE_URL_ + url, headers=_REQ_HEADERS_)
        doc = pq(response.text)
        import re
        url_primary_html_document = doc('a[href*="xml"]').eq(0).attr('href')  # Html primary doc is 1st in the list
        url_primary_document = doc('a[href*="xml"]').eq(1).attr('href')  # XML Primary doc is always 2nd in the list
        url_list_document = doc('a[href*="xml"]').eq(3).attr('href')  # xml list is always 4th in the list

        response = requests.get(_BASE_URL_ + url_primary_html_document, headers=_REQ_HEADERS_)
        primary_html_doc = pq(response.text)

        response = requests.get(_BASE_URL_ + url_primary_document, headers=_REQ_HEADERS_)
        primary_doc = pq(response.text)

        response = requests.get(_BASE_URL_ + url_list_document, headers=_REQ_HEADERS_)
        list_doc = pq(response.text)

        # Check if the documentation is to the nearest dollar or thousand dollars
        datetime_obj = datetime.strptime(date, '%Y-%m-%d')
        if datetime_obj.year < 2023:
            dollar_value_multiplier = 1000
        elif datetime_obj.year > 2023:
            dollar_value_multiplier = 1
        else:
            temp_list = primary_html_doc(':contains("nearest dollar")')
            if len(temp_list) > 0:
                dollar_value_multiplier = 1
            else:
                dollar_value_multiplier = 1000

        # Get primary doc detail
        filing_manager = self._get_bs4_text(primary_doc('filingManager name'))
        business_address = self._get_bs4_text(primary_doc('street1')) + ", " + self._get_bs4_text(primary_doc('city')) + ", " + self._get_bs4_text(primary_doc('stateOrCountry')) + ", " + self._get_bs4_text(primary_doc('zipCode'))
        submission_type = self._get_bs4_text(primary_doc('submissionType'))
        period_of_report = self._get_bs4_text(primary_doc('periodOfReport'))

        if self._get_bs4_text(primary_doc('amendmentInfo')) != 'N/A':  # Check if it is an amendment type filing
            amendment_type = self._get_bs4_text(primary_doc('amendmentInfo amendmentType'))
        else:
            amendment_type = 'N/A'

        signature_name = self._get_bs4_text(primary_doc('signatureBlock name'))
        signature_title = self._get_bs4_text(primary_doc('signatureBlock title'))
        signature_phone = self._get_bs4_text(primary_doc('signatureBlock phone'))
        signature_city = self._get_bs4_text(primary_doc('signatureBlock city'))
        signature_state = self._get_bs4_text(primary_doc('signatureBlock stateOrCountry'))
        signature_date = self._get_bs4_text(primary_doc('signatureBlock signatureDate'))

        portfolio_value = int(self._get_bs4_text(primary_doc('summaryPage tableValueTotal'))) * dollar_value_multiplier
        count_holdings = int(self._get_bs4_text(primary_doc('summaryPage tableEntryTotal')))

        filing_cover_page = {
            "filing_manager": filing_manager, 
            "business_address": business_address, 
            "submission_type": submission_type, 
            "period_of_report": period_of_report, 
            "signature_name": signature_name, 
            "signature_title": signature_title, 
            "signature_phone": signature_phone, 
            "signature_city": signature_city, 
            "signature_state": signature_state, 
            "signature_date": signature_date, 
            "amendment_type": amendment_type,
            "portfolio_value": portfolio_value, 
            "count_holdings": count_holdings, 
            "filing_amended": False  # Used to record if this instance of the filing has been amended in any way
        }

        # Get list doc detail
        list_of_holdings = list_doc('infoTable')
        result = []
        for each_holding in list_of_holdings.items():
            name_of_issuer = self._get_bs4_text(each_holding('nameOfIssuer'))
            title_of_class = self._get_bs4_text(each_holding('titleOfClass'))
            cusip = self._get_bs4_text(each_holding('cusip'))
            holding_value = int(each_holding('value').text()) * dollar_value_multiplier
            share_or_principal_amount = self._get_bs4_text(each_holding('shrsOrPrnAmt sshPrnamtType'))
            share_or_principal_amount_count = int(each_holding('shrsOrPrnAmt sshPrnamt').text())
            investment_discretion = self._get_bs4_text(each_holding('investmentDiscretion'))
            other_manager = self._get_bs4_text(each_holding('otherManager'))
            voting_authority_share_or_principal_amount_count_sole = int(each_holding('votingAuthority Sole').text())
            voting_authority_share_or_principal_amount_count_shared = int(each_holding('votingAuthority Shared').text())
            voting_authority_share_or_principal_amount_count_none = int(each_holding('votingAuthority None').text())

            result.append({
                "Name of issuer": name_of_issuer, 
                "Title of class": title_of_class, 
                "CUSIP": cusip,
                "Holding value": holding_value,
                "Share or principal type": share_or_principal_amount,
                "Share or principal amount count": share_or_principal_amount_count,
                "Put or call": None, 
                "Investment discretion": investment_discretion, 
                "Other manager": other_manager, 
                "Voting authority sole count": voting_authority_share_or_principal_amount_count_sole, 
                "Voting authority shared count": voting_authority_share_or_principal_amount_count_shared, 
                "Voting authority none count": voting_authority_share_or_principal_amount_count_none
            })
        
        holdings_table = pd.DataFrame.from_dict(result)

        simplified_columns = ['Name of issuer', 'Title of class', 'CUSIP', 'Share or principal type', 'Put or call', 'Holding value', 'Share or principal amount count']
        holdings_table_dropped_na = holdings_table[simplified_columns].dropna(axis=1)
        simplified_holdings_table = holdings_table_dropped_na.groupby(holdings_table_dropped_na.columns[:-2].to_list(), sort=False, as_index=False).sum()

        if self.manager == None:
            self.manager = filing_cover_page.get('filing_manager')

        return filing_cover_page, holdings_table, simplified_holdings_table

    def _apply_amendments(self, qtr_year_str:str, original_cover_page:dict, original_holdings_table:pd.DataFrame, original_simplified_holdings_table: pd.DataFrame):
        self._13f_amendment_filings_period_of_filings()
        select_amendment_filings = self._13f_amendment_filings[self._13f_amendment_filings['Period of Report Quarter Year'] == qtr_year_str].iloc[::-1]    # Check for matching amendments and reverse the order of the list so amendments can be made chronologically. 
        
        # Start by setting the output variables, this ensures that if no amendment filings are found, these can be returned as is, unaltered.
        output_cover_page = original_cover_page    # Set as original cover page to begin with
        output_holdings_table = original_holdings_table
        output_simplified_holdings_table = original_simplified_holdings_table
        
        if len(select_amendment_filings) > 0:
            for index, row in select_amendment_filings.iterrows():
                a_cover_page, a_holdings_table, a_simplified_holdings_table = self._parse_13f_url(row['url'], row['Filing Date'])
                if a_cover_page["amendment_type"] == "NEW HOLDINGS":

                    output_cover_page['portfolio_value'] = original_cover_page['portfolio_value'] + a_cover_page['portfolio_value']
                    output_cover_page['count_holdings'] = original_cover_page['count_holdings'] + a_cover_page['count_holdings']

                    # original_holdings_table = original_holdings_table.append(a_holdings_table, ignore_index=True)
                    output_holdings_table = pd.concat([original_holdings_table,a_holdings_table],ignore_index=True)
                    # original_simplified_holdings_table = original_simplified_holdings_table.append(a_simplified_holdings_table, ignore_index=True)
                    output_simplified_holdings_table = pd.concat([original_simplified_holdings_table,a_simplified_holdings_table], ignore_index=True)
                    output_cover_page['filing_amended'] = True
                else:   # If it is a not a "New Holdings" filing type, simply overwrite the entirety of the previous filing. 
                    output_cover_page = a_cover_page
                    output_holdings_table = a_holdings_table
                    output_simplified_holdings_table = a_simplified_holdings_table
                    output_cover_page['filing_amended'] = True
        return output_cover_page, output_holdings_table, output_simplified_holdings_table

    def convert_filings_to_excel(self, simplified:bool = True, inc_cover_page_tabs:bool = False):
        """Outputs existing 'self.filings' dictionary to excel. Note that this will overwrite any existing files that may be present."""
        table_type = "Simplified Holdings Table" if simplified == True else "Holdings Table"
        if len(self.filings)>0:
            if os.path.exists('{}.xlsx'.format(self.cik)):
                os.remove('{}.xlsx'.format(self.cik))
            with pd.ExcelWriter('{}.xlsx'.format(self.cik)) as writer: 
                for qtr_year in self.filings:
                    if inc_cover_page_tabs == True:
                        pd.DataFrame.from_dict(self.filings[qtr_year]['Cover Page'],orient='index').to_excel(writer,sheet_name="{}_cover_pg".format(qtr_year))
                    pd.read_json(self.filings[qtr_year][table_type]).to_excel(writer,sheet_name="{}_holdings".format(qtr_year))
        return        

    def get_latest_13f_filing(self, simplified:bool = True, amend_filing:bool = True):
        """Returns the latest 13F-HR filing."""
        self._get_last_100_13f_filings_url()
        # Grab latest 13F-HR filing, do not grab amendment filings ("13F-HR/A")
        url = self._13f_filings['url'][0]
        filing_date = self._13f_filings['Filing Date'][0]

        latest_13f_cover_page, latest_holdings_table, latest_simplified_holdings_table = self._parse_13f_url(url,filing_date)
        
        qtr_year_str = self._recent_qtr_year(self._13f_filings['Filing Date'][0])
        if amend_filing and len(self._13f_amendment_filings) > 0:
            latest_13f_cover_page, latest_holdings_table, latest_simplified_holdings_table = self._apply_amendments(qtr_year_str, latest_13f_cover_page, latest_holdings_table, latest_simplified_holdings_table)

        self.filings.update({
                        qtr_year_str:{
                            "Cover Page":latest_13f_cover_page, 
                            "Period of Report":latest_13f_cover_page['period_of_report'],
                            "Holdings Table":latest_holdings_table.to_json(), 
                            "Simplified Holdings Table":latest_simplified_holdings_table.to_json(), 
                            "Fund Value":latest_13f_cover_page['portfolio_value'], 
                            "Holdings Count":latest_13f_cover_page['count_holdings'],
                            "Simplified Holdings Count":len(latest_simplified_holdings_table),
                            "Latest 13F":True,
                            "Amended Filing":amend_filing
                            }})
        
        if simplified==True: 
            return latest_simplified_holdings_table
        else: 
            return latest_holdings_table
        
    def get_latest_13f_filing_cover_page(self):
        """Returns the latest 13F-HR filing cover page."""
        latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
        if len(latest_qtr_year) >0:
            return self.filings[latest_qtr_year[0]]['Cover Page']
        else:
            self.get_latest_13f_filing()
            latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
            return self.filings[latest_qtr_year[0]]['Cover Page']

    def get_latest_13f_value(self):
        """Returns the latest 13F-HR value of fund value"""
        latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
        if len(latest_qtr_year) >0:
            return self.filings[latest_qtr_year[0]]['Fund Value']
        else:
            self.get_latest_13f_filing()
            latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
            return self.filings[latest_qtr_year[0]]['Fund Value']

    def get_latest_13f_num_holdings(self, holdings_type:str = 'Simplified Holdings Count'):
        """Returns the latest 13F-HR number of holdings"""
        latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
        if len(latest_qtr_year) >0:
            return self.filings[latest_qtr_year[0]][holdings_type]
        else:
            self.get_latest_13f_filing()
            latest_qtr_year = [x for x in self.filings.keys() if self.filings[x]['Latest 13F']]
            return self.filings[latest_qtr_year[0]][holdings_type]

    def get_13f_filing(self, cal_qtr_year:str, amend_filing:bool=True):
        """Returns the requested 13F-HR filing."""
        self._get_last_100_13f_filings_url()
        if len(self.filings) != 0:
            if cal_qtr_year in self.filings:
                return self.filings[cal_qtr_year]["Cover Page"], pd.read_json(self.filings[cal_qtr_year]["Holdings Table"]), pd.read_json(self.filings[cal_qtr_year]["Simplified Holdings Table"])
        filing_url_date = None
        latest_13_f_filing = False
        for index, row in self._13f_filings.iterrows():
            datetime_obj = datetime.strptime(row['Filing Date'], '%Y-%m-%d')
            quarter_dict = {1:4, 2:1, 3:2, 4:3} # Every statement released is for the previous quarter.
            release_qtr = quarter_dict[(datetime_obj.month - 1)//3 + 1]
            year = datetime_obj.year
            if release_qtr == 4:    # Anything released in the previous quarter will have a year of last year (e.g. report is for 31st Dec 2022, yet report was released on the 1st Feb 2023)
                year = year - 1

            if "Q{}-{}".format(release_qtr, year) == cal_qtr_year:
                filing_url_date = row['Filing Date']
                filing_url = row['url']
                if index == 0:
                    latest_13_f_filing = True
        
        
        if filing_url_date == None:
            raise Exception("No filing could be found for the period {}".format(cal_qtr_year))

        cover_page, holdings_table, simplified_holdings_table = self._parse_13f_url(filing_url, filing_url_date)
        
        qtr_year_str = self._recent_qtr_year(filing_url_date)
        if amend_filing and len(self._13f_amendment_filings)>0:
            cover_page, holdings_table, simplified_holdings_table = self._apply_amendments(qtr_year_str, cover_page, holdings_table, simplified_holdings_table)
        
        self.filings.update({
                        cal_qtr_year:{
                            "Cover Page":cover_page, 
                            "Period of Report":cover_page['period_of_report'],
                            "Holdings Table":holdings_table.to_json(), 
                            "Simplified Holdings Table":simplified_holdings_table.to_json(), 
                            "Fund Value":cover_page['portfolio_value'], 
                            "Holdings Count":cover_page['count_holdings'],
                            "Simplified Holdings Count":len(simplified_holdings_table),
                            "Latest 13F":latest_13_f_filing}})

        return cover_page, holdings_table, simplified_holdings_table

    
    