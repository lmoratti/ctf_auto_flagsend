import requests
import time
import json
import os
import subprocess
import argparse

parser = argparse.ArgumentParser(description='A helper script to automate sending the flags to the server. The script reads from environment variables. They are sent every 1 minute. You probably want to use other bash scripts or python scripts to automate setting those variables. Environment variable should be similar to TEAM1_FLAG1.\nUsage: export TOKEN={Session_Cookie_Value_From_RTA_Website} \n Python3 ctf_automate_flagsend -t $TOKEN')

parser.add_argument('--submit_url', metavar='u', type=str, default="https://redteamassociation.com/submit", 
                            help='The submission URL. Default "https://redteamassociation.com/submit"')
parser.add_argument('-token', metavar='t', type=str, help='The session token to submit')
parser.add_argument('--sleep', metavar='s', type=int, default=55, help='The sleep interval to use. Default is 55 secs.')
parser.add_argument('--number_of_teams', metavar='tn', type=int, default=6, help='Number of teams participating. Default 6.')
parser.add_argument('--flags_per_team', metavar='f', type=int, default=4, help='Flags per team. Default 4.')
parser.add_argument('--env_updater_script', metavar='u', type=str, default="update_env.sh", 
                            help='Path to a script to update environment variables with flags.')

# Configuration
args            = parser.parse_args()
URL             = args.submit_url
TEAM_TOKEN      = args.token
HEADERS         = {"Cookie": f"session={TEAM_TOKEN}"}
SLEEP_INTERVAL  = args.sleep
NUMBER_OF_TEAMS = args.number_of_teams + 1
FLAGS_PER_TEAM  = args.flags_per_team + 1
UPDATER_SCRIPT  = args.env_updater_script


class Team:
    def __init__(self: 'Team', team_number: int, flag_count: int):
        self.team_number: str    = f"TEAM{team_number}"
        self.flags: Dictionary   = {}
        self.FLAGS_COUNT: int    = flag_count
       
    def _load_flags(self: 'Team')-> None:
        """Load environment variables for the teams flags"""

        for flag_number in range(1, self.FLAGS_COUNT):
             self.flags[flag_number] = os.getenv(f'{self.team_number}_FLAG{flag_number}', '_not_found')
 
    def _send_flag(self: 'Team', flag_number: int, flag_data: str)-> None:
        """Send a single flag to the CTF server. Used internally by the class"""

        if flag_data == '_not_found':
            print(f"""\033[31mNo flag in {self.team_number}_FLAG{flag_number} environment variable.\033[0m""") 
            return

        print(f"Flag found in {self.team_number}_FLAG{flag_number}!")
        data     = {'flag': flag_data}
        response = requests.post(URL, headers=HEADERS, data=data)

        if response.status_code == 200:
            server_response = json.loads(response.text)['message']
            if server_response   == 'Flag not found':
                print(f"\033[33m\t{server_response} or was already submitted. \033[0m") 
            elif server_response == 'Flag submitted successfully':
                print(f"\033[32m\t{server_response} \033[0m")
        else: 
            print("Failed to get 200 response from scoreboard URL. Check session token.")
            return

    def send_flags(self: 'Team') -> None:
        """Send all the flags for the team. """
        self._load_flags()
        for flag_num in range(1, self.FLAGS_COUNT):
                self._send_flag(flag_num, self.flags[flag_num])           

def main():
    teams: List = []
    for team_number in range(1, NUMBER_OF_TEAMS):
       teams.append(Team(team_number, FLAGS_PER_TEAM))
    
    while True:
        try:
            #Run the updater script and capture the output
            output = subprocess.check_output(f"bash {UPDATER_SCRIPT} && env", shell=True, text=True)

            # Parse the output to update the environment variables
            env_updates = dict(line.split("=", 1) for line in output.splitlines() if 'FLAG' in line)
            os.environ.update(env_updates)

        except subprocess.CalledProcessError as e:
            print(f"Failure in running {UPDATER_SCRIPT}. Might need you to fix it.")
            print(e)

        for team in teams:
            team.send_flags()
        print(f"{time.strftime("%H:%M:%S", time.localtime())}: Sleeping for {SLEEP_INTERVAL} seconds.")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()

