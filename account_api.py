import paramiko

try :
    from secret_account import username, password
    from secret_hostname import hostname
except :
    from bak.secret_account import username, password
    from bak.secret_hostname import hostname


class ActiveDirectory:
    def __init__(self):
        self.username = username
        self.password = password
        self.hostname = hostname
        dc1 = paramiko.SSHClient()
        dc1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        dc1.connect(self.hostname, 22, self.username, self.password)
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
            cmd_unlock = f"net user '{accountname}'"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_unlock)
            errmsg = stderr.read().decode('big5')
            queryresult = stdout.read().decode('big5').split('\n')[9]
            stdin.close()
            if errmsg == '' :
                return f"帳號名 : {accountname}\n{queryresult}"
            else :
                return errmsg.split('\n')[0]
        except :
            return f"{self.hostname} connecting failure !"

    def Account_unlocker(self, accountname):
        if accountname == "" :
            return "帳號不可為空"
        try :  
            cmd_unlock = f"powershell Unlock-ADAccount -Identity '{accountname}'"
            stdin, stdout, stderr = self.dc1.exec_command(cmd_unlock)
            errmsg = stderr.read().decode('big5')
            stdin.close()
            if errmsg == '' :
                return f"Unlock Account : {accountname} success"
            else :
                return errmsg.split('\n')[0]
        except :
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
        except :
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
        except :
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
        except :
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
        except :
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
        except :
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
        except :
            return f"{self.hostname} connecting failure !"

    def __del__(self):
        self.dc1.close()

if __name__ == "__main__" :
    a = ActiveDirectory()
    x = a.Account_expire_date('alex.li')
    print(x)
