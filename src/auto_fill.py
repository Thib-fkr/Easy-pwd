
from yaml import load, Loader

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

from manager import Manager as Man

def main():
    
    man = Man()
    
    # Firefox has to be launched with --marionette arg
    driver = webdriver.Firefox(service=Service(executable_path="selenium-driver/geckodriver", service_args=["--marionette-port", "2828", "--connect-existing"]))
    
    # Get active url
    url = driver.current_url
    
    # Retrieve websites list
    with open("data/sites/0.yml") as f:
        enc_sites : list[dict[int, dict]] = load(f, Loader=Loader)["website"]

    # Look through each website name to find if one corresponds to the active url
    for enc_site in enc_sites[1:]:
        
        # Store associated file number and isolate useful data
        for number in enc_site.keys():
            enc_site_2 = enc_site[number]
        
        clear_site = man.decrypt(hash=enc_site_2["hash"], salt=enc_site_2["salt"])
        
        # Load and decrypt authentication information from correct file
        if clear_site.decode() == url:
            with open(f"data/sites/{number}.yml") as f:
                enc_auth : dict = load(f, Loader=Loader)
            clear_auth = \
                (man.decrypt(hash=enc_auth["username"], salt=enc_auth["salt1"]).decode() , \
                man.decrypt(hash=enc_auth["password"], salt=enc_auth["salt2"]).decode())
            
            driver.find_element(by=By.NAME, value="username").send_keys(clear_auth[0])
            
            driver.find_element(by=By.NAME, value="pwd").send_keys(clear_auth[1])
            
            

if __name__ == "__main__":
    main()