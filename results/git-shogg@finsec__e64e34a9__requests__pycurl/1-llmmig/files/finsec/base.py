import pycurl
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import pdb
import os
import time
from io import StringIO, BytesIO

_BASE_URL_ = 'https://www.sec.gov'
_13F_SEARCH_URL_ = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=13F-HR&count=100'
_REQ_HEADERS_ = [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'Accept-Encoding: gzip, deflate, br',
    'HOST: www.sec.gov',
]

class FilingBase():
    def __init__(self, cik, declared_user=None):
        if declared_user is not None:
            _REQ_HEADERS_[0] = f'User-Agent: {declared_user}; {_REQ_HEADERS_[0][12:]}'
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

    def _make_request(self, url):
        """Helper function to make HTTP GET requests using pycurl."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, buffer)
            curl.setopt(pycurl.HTTPHEADER, _REQ_HEADERS_)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.perform()
            curl.close()
        except pycurl.error as e:
            curl.close()
            raise Exception(f"An error occurred while making the request: {e}")
        return buffer.getvalue().decode('utf-8')

    def _get_last_100_13f_filings_url(self):
        """Searches the last 13F-HR and 13F-HR/A filings. Returns a 13f_filings variable and 13f_amendment_filings variable"""
        if self._13f_filings is not None or self._13f_amendment_filings is not None:
            return

        webpage_content = self._make_request(_13F_SEARCH_URL_.format(self.cik))
        soup = bs(webpage_content, "html.parser")
        results_table = soup.find(lambda table: table.has_attr('summary') and table['summary'] == "Results")
        results_table_df = pd.read_html(StringIO(str(results_table)))[0]
        
        url_endings = []
        url_link_col = results_table_df.columns.get_loc("Format")
        for row in results_table.find_all('tr'):
            tds = row.find_all('td')
            try:
                url_endings.append(tds[url_link_col].find('a')['href'])
            except:
                pass
        results_table_df['url'] = url_endings
        self._13f_filings = results_table_df[results_table_df['Filings'] == "13F-HR"].reset_index(drop=True)
        self._13f_amendment_filings = results_table_df[results_table_df['Filings'] == "13F-HR/A"].reset_index(drop=True)

        return self._13f_filings, self._13f_amendment_filings
    
    def _13f_amendment_filings_period_of_filings(self):
        """This function finds the actual 'period of report' for the 13f amendment filings (this function needs to open the filing url for each and every 13f amendment identified). This is required to understand which particular report is being amended."""
        def _pandas_apply_func(x):
            webpage_content = self._make_request(_BASE_URL_ + x['url'])
            soup = bs(webpage_content, "html.parser")
            period_of_report_div = soup.find('div', text='Period of Report')
            period_of_report_date = period_of_report_div.find_next_sibling('div', class_='info').text
            datetime_obj = datetime.strptime(period_of_report_date, '%Y-%m-%d')
            release_qtr = datetime_obj.month // 3
            year = datetime_obj.year
            time.sleep(0.2)
            return pd.Series([period_of_report_date, "Q{}-{}".format(release_qtr, year)]) 
        self._13f_amendment_filings[['Period of Report', 'Period of Report Quarter Year']] = self._13f_amendment_filings.apply(_pandas_apply_func, axis=1)
        return self._13f_amendment_filings       

    def _parse_13f_url(self, url:str, date:str):
        webpage_content = self._make_request(_BASE_URL_ + url)
        soup = bs(webpage_content, "html.parser")
        import re
        url_primary_html_document = soup.find_all('a', attrs={'href': re.compile('xml')})[0]['href']  # Html primary doc is 1st in the list, this contains the detail on whether the dollars listed are nearest dollar or thousand dollar.
        url_primary_document = soup.find_all('a', attrs={'href': re.compile('xml')})[1]['href']  # XML Primary doc is always 2nd in the list.
        url_list_document = soup.find_all('a', attrs={'href': re.compile('xml')})[3]['href']  # xml list is always 4th in the list.

        primary_html_doc_content = self._make_request(_BASE_URL_ + url_primary_html_document)
        primary_html_doc = bs(primary_html_doc_content, "xml")

        primary_doc_content = self._make_request(_BASE_URL_ + url_primary_document)
        primary_doc = bs(primary_doc_content, "xml")

        list_doc_content = self._make_request(_BASE_URL_ + url_list_document)
        list_doc = bs(list_doc_content, "xml")

        # Check if the documentation is to the nearest dollar or thousand dollars. This new reporting rule came into effect in 2023 (reference: https://www.sec.gov/info/edgar/specifications/form13fxmltechspec)
        datetime_obj = datetime.strptime(date, '%Y-%m-%d')
        if datetime_obj.year < 2023:
            dollar_value_multiplier = 1000
        elif datetime_obj.year > 2023:
            dollar_value_multiplier = 1
        else:
            temp_list = primary_html_doc.findAll(text=re.compile('nearest dollar'))
            if len(temp_list) > 0:
                dollar_value_multiplier = 1
            else:
                dollar_value_multiplier = 1000

        # Get primary doc detail
        filing_manager = self._get_bs4_text(primary_doc.find("filingManager").find("name"))
        business_address = self._get_bs4_text(primary_doc.find("street1")) + ", " + self._get_bs4_text(primary_doc.find("city")) + ", " + self._get_bs4_text(primary_doc.find("stateOrCountry")) + ", " + self._get_bs4_text(primary_doc.find("zipCode"))
        submission_type = self._get_bs4_text(primary_doc.find("submissionType"))
        period_of_report = self._get_bs4_text(primary_doc.find("periodOfReport"))

        if self._get_bs4_text(primary_doc.find("amendmentInfo")) != 'N/A':  # Check if it is an amendment type filing.
            amendment_type = self._get_bs4_text(primary_doc.find("amendmentInfo").find("amendmentType"))
        else:
            amendment_type = 'N/A'

        signature_name = self._get_bs4_text(primary_doc.find("signatureBlock").find("name"))
        signature_title = self._get_bs4_text(primary_doc.find("signatureBlock").find("title"))
        signature_phone = self._get_bs4_text(primary_doc.find("signatureBlock").find("phone"))
        signature_city = self._get_bs4_text(primary_doc.find("signatureBlock").find("city"))
        signature_state = self._get_bs4_text(primary_doc.find("signatureBlock").find("stateOrCountry"))
        signature_date = self._get_bs4_text(primary_doc.find("signatureBlock").find("signatureDate"))

        portfolio_value = int(self._get_bs4_text(primary_doc.find("summaryPage").find("tableValueTotal"))) * dollar_value_multiplier
        count_holdings = int(self._get_bs4_text(primary_doc.find("summaryPage").find("tableEntryTotal")))

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
            "filing_amended": False                  # Used to record if this instance of the filing has been amended in any way. 
        }

        # Get list doc detail
        list_of_holdings = list_doc.findAll("infoTable")
        result = []
        for each_holding in list_of_holdings:
            name_of_issuer = self._get_bs4_text(each_holding.find("nameOfIssuer"))
            title_of_class = self._get_bs4_text(each_holding.find("titleOfClass"))
            cusip = self._get_bs4_text(each_holding.find("cusip"))
            holding_value = int(each_holding.find("value").text) * dollar_value_multiplier
            share_or_principal_amount = self._get_bs4_text(each_holding.find("shrsOrPrnAmt").find("sshPrnamtType"))
            share_or_principal_amount_count = int(each_holding.find("shrsOrPrnAmt").find("sshPrnamt").text)
            # put_or_call = each_holding.find("SOMETHING").text
            investment_discretion = self._get_bs4_text(each_holding.find("investmentDiscretion"))
            other_manager = self._get_bs4_text(each_holding.find("otherManager"))
            voting_authority_share_or_principal_amount_count_sole = int(each_holding.find("votingAuthority").find("Sole").text)
            voting_authority_share_or_principal_amount_count_shared = int(each_holding.find("votingAuthority").find("Shared").text)
            voting_authority_share_or_principal_amount_count_none = int(each_holding.find("votingAuthority").find("None").text)

            result.append({"Name of issuer": name_of_issuer, "Title of class": title_of_class, "CUSIP": cusip, "Holding value": holding_value, "Share or principal type": share_or_principal_amount, "Share or principal amount count": share_or_principal_amount_count, "Put or call": None, "Investment discretion": investment_discretion, "Other manager": other_manager, "Voting authority sole count": voting_authority_share_or_principal_amount_count_sole, "Voting authority shared count": voting_authority_share_or_principal_amount_count_shared, "Voting authority none count": voting_authority_share_or_principal_amount_count_none})
        
        holdings_table = pd.DataFrame.from_dict(result)

        simplified_columns = ['Name of issuer', 'Title of class', 'CUSIP', 'Share or principal type', 'Put or call', 'Holding value', 'Share or principal amount count']
        holdings_table_dropped_na = holdings_table[simplified_columns].dropna(axis=1)
        simplified_holdings_table = holdings_table_dropped_na.groupby(holdings_table_dropped_na.columns[:-2].to_list(), sort=False, as_index=False).sum()

        if self.manager == None:
            self.manager = filing_cover_page.get('filing_manager')

        return filing_cover_page, holdings_table, simplified_holdings_table
