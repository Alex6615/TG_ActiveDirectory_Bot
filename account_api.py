import paramiko
import logging

# ENV
import os
HOST16 = os.getenv(key='HOST16')
HOST34 = os.getenv(key='HOST34')
AD_USERNAME = os.getenv(key='AD_USERNAME')
AD_PASSWD = os.getenv(key='AD_PASSWD')

class ActiveDirectory:
    def __init__(self, host=HOST34):
        self.username = AD_USERNAME
        self.password = AD_PASSWD
        self.hostname = host
        logging.info(f"{self.username}-{self.hostname}")
        print(f"{self.username}-{self.hostname}")
        dc1 = paramiko.SSHClient()
        dc1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        x = dc1.connect(self.hostname, 22, self.username, self.password, timeout=10)
        self.dc1 = dc1
        self.exceptTargets = [
            'exporter', 
            'ranchadmin',
            'vpn_auth',
            'openvpn', 
        ]

    def Account_expire_date(self, accountname):
        if accountname == "" :
            return "帳號不可為空"
        try :  
            cmd_unlock = f"net user {accountname}"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_unlock)
            errmsg = stderr.read().decode('big5')
            queryresult = stdout.read().decode('big5').split('\n')[9]
            stdin.close()
            if errmsg == '' :
                return f"帳號名 : {accountname}\n{queryresult}"
            else :
                return errmsg.split('\n')[0]
        except Exception as e :
            logging.info(e)
            return f"{self.hostname} connecting failure !"

    def Account_unlocker(self, accountname):
        if accountname == "" :
            return "帳號不可為空"
        cmd_unlock = f"Unlock-ADAccount -Identity {accountname}"
        stdin, stdout, stderr = self.dc1.exec_command(cmd_unlock, timeout=10)
        try :  
            cmd_unlock = f"powershell Unlock-ADAccount -Identity '{accountname}'"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_unlock, timeout=10)
            errmsg = stderr.read().decode('big5')
            stdin.close()
            if errmsg == '' :
                return f"Unlock Account : {accountname} success"
            else :
                print(stdout.read().decode('big5'))
                print(errmsg)
                return errmsg.split('\n')[0]
        except Exception as e :
            print("exception")
            logging.info(e)
            print("exception end")
            return f"{self.hostname} connecting failure !"

    def Account_disabler(self, accountname):
        if accountname == "" :
            return "帳號不可為空"
        try :  
            cmd_disable = f"powershell Disable-ADAccount -Identity '{accountname}'"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_disable)
            errmsg = stderr.read().decode('big5')
            stdin.close()
            if errmsg == '' :
                return f"Disable Account : {accountname} success"
            else :
                return errmsg.split('\n')[0]
        except Exception as e :
            logging.info(e)
            return f"{self.hostname} connecting failure !"

    def Account_enabler(self, accountname):
        if accountname == "" :
            return "帳號不可為空"
        try :
            cmd_disable = f"powershell Enable-ADAccount -Identity '{accountname}'"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_disable)
            errmsg = stderr.read().decode('big5')
            stdin.close()
            if errmsg == '' :
                return f"Enable Account : {accountname} success"
            else :
                return errmsg.split('\n')[0]
        except Exception as e :
            print(e)
            return f"{self.hostname} connecting failure !"

    def Account_Password_Reset(self, accountname):
        if accountname == "" :
            return "帳號不可為空"
        try :  
            reset_password = f"$password = '1qazXSW@' ; Set-ADAccountPassword {accountname} -Reset -NewPassword (ConvertTo-SecureString -AsPlainText  $password -Force -Verbose) –PassThru"
            self.Account_enabler(accountname)
            stdin, stdout, stderr = self.dc1.exec_command(reset_password)
            errmsg = stderr.read().decode('big5').split('\n')[0]
            stdin.close()
            if errmsg == '' :
                return f"Reset Account : {accountname} success"
            else :
                return errmsg.split('\n')[0]
        except Exception as e :
            logging.info(e)
            return f"{self.hostname} connecting failure !"

    def user_List(self):
        result = []
        try :  
            cmd_all = f"dsquery user -limit 0 -o samid OU=company,DC=owin,DC=corp"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_all)
            userAll = stdout.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            cmd_resign = f"dsquery user -limit 0 -o samid OU=resign,OU=company,DC=owin,DC=corp"
            stdin2, stdout2, stderr2 = self.dc1.exec_command(cmd_resign)
            userResign = stdout2.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            # Union without repeat
            set1 = set(self.exceptTargets)
            set2 = set(userResign)
            userNeedExcept = list(set1.union(set2))
            ###
            for i in range(0, len(userAll)) :
                #if userAll[i] not in userNeedExcept :
                if userAll[i] not in userNeedExcept :
                   result.append(userAll[i]) 
            return sorted(result)
        except Exception as e :
            logging.info(e)
            return f"{self.hostname} connecting failure !"

    def user_List_enabled(self):
        result = []
        try :  
            cmd_all = f"dsquery user -limit 0 -o samid OU=company,DC=owin,DC=corp"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_all)
            userAll = stdout.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            cmd_disabled = f"dsquery user -limit 0 -o samid OU=company,DC=owin,DC=corp -disabled"
            stdin, stdout2, stderr = self.dc1.exec_command(cmd_disabled)
            userDisabled = stdout2.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            cmd_resign = f"dsquery user -limit 0 -o samid OU=resign,OU=company,DC=owin,DC=corp"
            stdin2, stdout2, stderr2 = self.dc1.exec_command(cmd_resign)
            userResign = stdout2.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            #Union without repeat
            set1 = set(self.exceptTargets)
            set2 = set(userDisabled)
            set3 = set(userResign)
            userNeedExcept = list(set1.union(set2.union(set3)))
            ###
            for i in range(0, len(userAll)) :
                if userAll[i] not in userNeedExcept :
                   result.append(userAll[i]) 
            return sorted(result)
        except Exception as e :
            logging.info(e)
            return f"{self.hostname} connecting failure !"

    def user_List_disabled(self):
        result = []
        try :  
            cmd_resign = f"dsquery user -limit 0 -o samid OU=resign,OU=company,DC=owin,DC=corp"
            stdin2, stdout2, stderr2 = self.dc1.exec_command(cmd_resign)
            userResign = stdout2.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            cmd_disabled = f"dsquery user -limit 0 -o samid OU=company,DC=owin,DC=corp -disabled"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_disabled)
            userDisabled = stdout.read().decode('big5').replace('\r', '').replace('\"', '').split('\n')
            #Union without repeat
            set1 = set(self.exceptTargets)
            set2 = set(userResign)
            userNeedExcept = list(set1.union(set2))
            ###
            for i in range(0, len(userDisabled)) :
                #if userAll[i] not in userNeedExcept :
                if userDisabled[i] not in userNeedExcept :
                   result.append(userDisabled[i]) 
            return sorted(result)
        except Exception as e :
            logging.info(e)
            return f"{self.hostname} connecting failure !"

    def __del__(self):
        self.dc1.close()
        logging.info(f"SSH Conn to -{self.hostname}- Closed !")

if __name__ == "__main__" :
    a = ActiveDirectory(host=HOST16)
    #x = a.Account_unlocker('leo.c')
    #x = a.Account_enabler('leo.c')
    #x = a.Account_Password_Reset('test69')
    #x = a.Account_enabler('test69')
    #x = a.Account_expire_date('leo.c')
    #x = a.Account_unlocker('test69')
    #x = a.Account_enabler('test69')
    #print(x)
