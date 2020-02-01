import re
import os
import time

from common import insert_to_googlesheet

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


class GetRealtorsDetails(object):
	def __init__(self):
		self.base_url = 'https://secure.centris.ca/Authentification.aspx?application=89273393-7473-4256-b88e-f80044068f32&langue=en&callbackUrl=https%3a%2f%2faccounts.centris.ca%3a443%2faccount%2flogin-callback%3freturnUrl%3d%252fconnect%252fauthorize%253fclient_id%253dportal.centris.ca%2526redirect_uri%253dhttps%25253A%25252F%25252Fzone.centris.ca%25252Fsignin-oidc%2526response_type%253dcode%2526scope%253dopenid%252520profile%252520email%252520roles%252520offline_access%2526response_mode%253dform_post%2526nonce%253d637158656010112624.MDE1OTFlNzEtYmY1Yy00ZDYwLWE2YmEtMGYxMzUxNWQ4MWU4Y2E5MmQ1YmQtZDRjNy00NzQ4LWI1YmQtZTk0YTk1ZDAxMGI0%2526legacy_centris_token%253d%2526lang%253den%2526state%253dCfDJ8HHH6i3F_-hArFf24MwWzuXm5A0ArN7XaR1vj5kvX-SSmOP-lvt-kL8M68K3DZILiz9vUduqdds6prCdbt9PD3gl-AhNo0oS77JHNcfOUClef3k_jlKiSvHOMTr5WcpjEqAEXC5mXw7c92EjwpK9fsaj4HQ7fo0NDx19ahTCCDewF72rrE98nd9KpjZd5H6J97RV7Meqw4htIjqGWX15hOCMcVqH7T5ymkV2Nx84Bv2c4bZ3U3XflPBI4BM0RR3NOlgtekjGy-31TRGkfEku6mwOvVtir9XRS27eBkhDsXv7%2526x-client-SKU%253dID_NETSTANDARD2_0%2526x-client-ver%253d5.3.0.0'

		self.setup_driver('/home/john/Work/Test_Task/QuebecRealtors/chromedriver')
	
	def setup_driver(self, chrome_path, headless=False):
		"""
		Chreates chrome web driver.
		:chrome_path: the location of chromedriver.exe
		"""
		options = webdriver.ChromeOptions()

		if headless:
			options.add_argument('--headless')
		options.add_extension('/home/john/Documents/repack/LastPass_-Free-Password-Manager_v4.41.0.crx')

		self.driver = webdriver.Chrome(chrome_path, chrome_options = options)

		time.sleep(20)
	def is_visible_element(self, by_type, locator, timeout=10):
		"""
		Return true if locator is found up to timeout.
		Return false if it's not found until timeout is over.
		"""
		try:
			if by_type == 'name':
				WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.NAME, locator)))
			elif by_type == 'id':
				WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator)))
			else:
				WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
			return True
		except Exception as error:
			return False

	def start_process(self):
		"""
		Start automation process.
		"""
		# self.driver.get(self.base_url)
		self.driver.get("https://zone.centris.ca/Tools/membersdirectorytool/Redirect?IsCalledByIFrame=True&amp;ActionIndex=0&amp;ActionType=MainLink")
		print('Started automation')

		# replies = []
		# from_date = '2019-11-07'
		# to_date = '2019-11-09'

		if not self.is_visible_element('id', 'contenu_BtRecherche'):
			return False
		
		self.driver.find_element_by_id('contenu_BtRecherche').click()
		time.sleep(3)

		results = []
		start_index = 780
		temp_index = 0

		while True:
			if len(results) > 1000:
				break
			if temp_index < 80:
				time.sleep(5)
				table = self.driver.find_element_by_id("contenu_GridResultat_ctl01")
				table.find_element_by_css_selector("[title='Next page']").click()
				temp_index += 1
				continue
			time.sleep(3)
			tr_list = self.driver.find_elements_by_css_selector("#contenu_GridResultat_ctl01 tbody tr")
			for index in range(10):
				tr_list = self.driver.find_elements_by_css_selector("#contenu_GridResultat_ctl01 tbody tr")
				tr_list[index].click()

				time.sleep(3)

				realtors_info = []

				tr_list = self.driver.find_elements_by_css_selector("#contenu_GridResultat_ctl01 tbody tr")
				realtors_info.append(tr_list[index].find_elements_by_tag_name('td')[1].text)
				realtors_info.append(tr_list[index].find_elements_by_tag_name('td')[0].text)

				try:
					member_panel = self.driver.find_element_by_id('contenu_FicheMembrePanel')
					lg_id = member_panel.find_element_by_id('contenu_LinkLangueParlee')
					lg_id.click()

					self.is_visible_element('id', 'RadWindowContentFramecontenu_winManager_winLangue')
					first_iframe = self.driver.find_element_by_id('RadWindowContentFramecontenu_winManager_winLangue')
					self.driver.switch_to.frame(first_iframe)
					self.is_visible_element('id', 'BannerFrame')

					iframe = self.driver.find_element_by_id('BannerFrame')
					self.driver.switch_to.frame(iframe)
					self.is_visible_element('id', 'bllLangue')
					
					realtors_info.append(','.join([element.text.strip() for element in self.driver.find_elements_by_css_selector("#bllLangue li")]))

					self.driver.switch_to.default_content()
					WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'RadWindowContentFramecontenu_winManager_winLangue')))
					first_iframe = self.driver.find_element_by_id('RadWindowContentFramecontenu_winManager_winLangue')
					self.driver.switch_to.frame(first_iframe)
					self.driver.find_element_by_id('lnkClose').click()

					self.driver.switch_to.default_content()
				except:
					try:
						member_panel = self.driver.find_element_by_id('contenu_FicheMembrePanel')
						member_panel_content = member_panel.find_element_by_class_name('alterne').find_elements_by_tag_name('td')[1]
						realtors_info.append(re.search(r'Langue\s?: (.*?)\n', member_panel_content.text).group(1).strip())
					except:
						import pdb;
						pdb.set_trace()
				# time.sleep(2)
				member_panel = self.driver.find_element_by_id('contenu_FicheMembrePanel')

				try:
					self.is_visible_element('id', 'contenu_Line2')
					realtors_info.append(member_panel.find_element_by_id('contenu_Line2').text)
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_EmailMembre')
					realtors_info.append(member_panel.find_element_by_id('contenu_EmailMembre').get_attribute('href').split(':')[-1].strip())
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_LblTelephone1')
					realtors_info.append(member_panel.find_element_by_id('contenu_LblTelephone1').text)
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_LienNomBureau')
					realtors_info.append(member_panel.find_element_by_id('contenu_LienNomBureau').text)
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_courtier')
					realtors_info.append(member_panel.find_element_by_id('contenu_courtier').text)
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_lienAdresse')
					realtors_info.append(member_panel.find_element_by_id('contenu_lienAdresse').text.strip())
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_LblTelBureau')
					realtors_info.append(member_panel.find_element_by_id('contenu_LblTelBureau').text.strip())
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_LblFaxBureau')
					realtors_info.append(member_panel.find_element_by_id('contenu_LblFaxBureau').text.strip())
				except:
					realtors_info.append('')
				try:
					self.is_visible_element('id', 'contenu_WebBureau')
					realtors_info.append(member_panel.find_element_by_id('contenu_WebBureau').get_attribute('href'))
				except:
					realtors_info.append('')
 
				results.append(realtors_info)
				
				if len(results) % 20 == 0:
					insert_to_googlesheet(results[-20:], start_index)
					start_index += 20
					print("{} records are inserted into google sheet!".format(start_index))

				print(realtors_info)

			# self.driver.execute_script("RadGridNamespace.AsyncRequest('ctl00$contenu$GridResultat$ctl01$ctl03$ctl01$ctl12','', 'contenu_GridResultat', event)")
			table = self.driver.find_element_by_id("contenu_GridResultat_ctl01")
			table.find_element_by_css_selector("[title='Next page']").click()
			

if __name__ == '__main__':
	getrealtorsdetails = GetRealtorsDetails()
	getrealtorsdetails.start_process()