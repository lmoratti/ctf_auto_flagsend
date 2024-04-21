import requests
import time
import os

# Configuration
URL            = "https://redteamassociation.com/submit"  
TEAM_TOKEN     = "your_team_token_here"  
TEAM_TOKEN     = "eyJ0ZWFtX25hbWUiOiJ0ZWFtMSJ9.ZiVokA.dBZc8l2vWzFfOnjrmg_D-_LlQQY"
HEADERS        = {"Cookie": f"session={TEAM_TOKEN}"}
SLEEP_INTERVAL = 55

def send_flag(flag_number: int, flag_data: str)-> None:
    """Send a single flag to the CTF server."""
    if flag_data == 'default_value_if_not_found':
        print(f"""\033[31m 
No value in FLAG_{flag_number} in environment variable.
	Use "export FLAG_{flag_number}='flag' "
	You may wish to also use a script to automate your exploits and set that variable.
	Flags refresh every minute to reward persistence on other teams.
	""") 
        return

    data     = {'flag': flag_data}
    response = requests.post(URL, headers=HEADERS, data=data)
    print(f"Flag for {flag_number} submitted. Response: {response.text}")
    

def main():
    while True:
	# Read from environment variables
        flag_1 = os.getenv('FLAG_1', 'default_value_if_not_found')
        flag_2 = os.getenv('FLAG_2', 'default_value_if_not_found')
        flag_3 = os.getenv('FLAG_3', 'default_value_if_not_found')
        flag_4 = os.getenv('FLAG_4', 'default_value_if_not_found')

	# Send the flags from env variables
        try:
            send_flag(1, flag_1)
            send_flag(2, flag_2)
            send_flag(3, flag_3)
            send_flag(4, flag_4)
        except:
            print("Error in sending a flag. Check session token.")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()

