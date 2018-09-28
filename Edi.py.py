import ftplib
from io import BytesIO 
import json
import socket
import io

class EDI:
    
    def __init__(self):
        global host,ftp
        host = "b85.f23.myftpupload.com"
        userName ="haider"
        password = "Coaches1!"
        ftp = ftplib.FTP(host,userName,password)
        
    def main(self):       
        subDirectories = []
        files = []        
        try:
            mainDirectory = "/COLDWHEREEDISYSTEM"
            subDirectories = ftp.nlst(mainDirectory)
            byteReading = BytesIO()
            
        except ftplib.error_perm:
            if str(resp) == "550 No files found":
                print ("No files in this directory")
            else:
                raise
        subDirectories.remove(".")
        subDirectories.remove("..")

        for subDirectory in subDirectories:
          try:
            innerDirectory = mainDirectory+ "/"+ subDirectory 
            files = ftp.nlst(innerDirectory)
            files.remove(".")
            files.remove("..")
          except ftplib.error_perm:
            if str(resp) == "550 No files found":
                print ("No files in this directory")
            else:
                raise
        
          for file in files:
              if (file == "output" or file == "in"):
                  files.remove("output")     
              elif(file.split('.')[1] == "edi"):
                  fileName = file.split('.')[0]
                  filepath = innerDirectory+"/"+file
                  ftp.retrbinary('RETR '+ filepath, byteReading.write)
                  readingFile = byteReading.getvalue().decode("utf-8")  
                  self.readingCurrentFile(readingFile,innerDirectory,fileName)
   
    def readingCurrentFile(self,readingFile,filepath,fileName):
        data = {}    
        loadNumber = readingFile.split('*')[2].split("G")[0]
        rdate = readingFile.split('*')[4]+ " "+ readingFile.split('*')[6]
        senderNumber = readingFile.split('*')[34].split("A")[0]
        weight = readingFile.split('*')[37]
        ssdate = readingFile.split('*')[26] +" "+readingFile.split('*')[28]
        userEmail = readingFile.split('*')[12]
        deviceserial =readingFile.split('*')[15].split(":")[1]
        mcnumber = readingFile.split('*')[18].split(":")[1]
        senderName = readingFile.split("*")[21]
        ssaddress = readingFile.split("*")[23]
        ai = readingFile.split('*')[40].split(":")[1]
        aa = readingFile.split('*')[43].split(":")[1]
        maxp = readingFile.split('*')[49].split(":")[1]
        minp = readingFile.split('*')[46].split(":")[1]
        minh = readingFile.split('*')[52].split(":")[1]
        maxh = readingFile.split('*')[55].split(":")[1]
        mint = readingFile.split('*')[58].split(":")[1]
        maxt = readingFile.split('*')[61].split(":")[1]
        trucknumber = readingFile.split('*')[64].split(":")[1]
        trailernumber = readingFile.split('*')[67].split(":")[1]
        trailersize = readingFile.split('*')[70].split(":")[1]
        commodity = readingFile.split('*')[73]
        pallet = readingFile.split('*')[75]
        receiverName = readingFile.split("*")[78]
        sraddress = readingFile.split("*")[80]
        sddate = readingFile.split("*")[83]+" "+readingFile.split("*")[85]
        receiverNumber = readingFile.split('*')[90]

        data['message_type'] = 'create_load'
        data['commodities'] =commodity
        data['weight'] =float(weight)
        data['mc_number'] =mcnumber
        data['trucking_company_name'] =senderName
        data['active_insurance']=bool(ai)
        data['active_authority']=bool(aa)
        data['min_temperature']=int(mint)
        data['max_temperature']=int(maxt)
        data['truck_number']=trucknumber
        data['trailer_number'] = int(trailernumber)
        data['trailer_size'] =trailersize
        data['driver_number'] =senderNumber
        data['min_pressure'] =int(minp)
        data['max_pressure'] =int(maxp)
        data['min_humidity'] =int(minh)
        data['max_humidity'] =int(maxh)
        data['pallet'] =int(pallet)
        data['shippment_to_name'] =receiverName
        data['shippment_to_phone'] =receiverNumber
        data['device_serial'] =deviceserial
        data['user_email'] = userEmail
        data['load_number'] = loadNumber
        data['pickup_location'] = ssaddress
        data['dropoff_location'] =sraddress
        data['shipment_start_time'] = ssdate
        data['estimated_dropoff_time'] = sddate
        data['required_dropoff_time'] = rdate
        self.tcpRequest(data,filepath,fileName)
        
    def tcpRequest(self,data,filepath,fileName):
        TCP_IP = '35.161.234.96'
        TCP_PORT = 9991
        BUFFER_SIZE = 1024
        json_data = json.dumps(data)
        MESSAGE = json_data
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.sendto(MESSAGE.encode(),(TCP_IP, TCP_PORT))
        data = s.recv(BUFFER_SIZE)
        s.close()

        responseInstring = data.decode("utf-8")
        json_acceptable_string = responseInstring.replace("'", "\"")
        dictionary = json.loads(json_acceptable_string)
      
        if(dictionary["status"] == "Success"):
          self.movingCurrentInputFile(filepath,fileName)
          self.directoryExistance("output",filepath,fileName)
        else:
          self.movingCurrentInputFile(filepath,fileName)
          self.directoryExistance("output",filepath,fileName)

    def directoryExistance(self,directoryName,filepath,fileName):
        outputDirectory =filepath+"/"+directoryName
        if directoryName in ftp.nlst(filepath):
            self.outputFile(outputDirectory,fileName)
        else:     
            ftp.mkd(outputDirectory)
            self.outputFile(outputDirectory,fileName)
    
    def movingCurrentInputFile(self,filePath, fileName):
            inputDirectory =filePath+"/in"            
            if "in" in ftp.nlst(filePath):
                ftp.rename(filePath+"/"+fileName+".edi", inputDirectory +"/"+fileName+".edi" )                
            else:     
                ftp.mkd(inputDirectory)
                ftp.rename(filePath+"/"+fileName+".edi", inputDirectory +"/"+fileName+".edi" )
                
       
    def outputFile(self,filepath,filename):
        ftp.cwd(filepath)
        output = io.BytesIO(b"""ISA*01*0000000000*01*0000000000*ZZ*ABCDEFGHIJKLMNO*ZZ*123456789012345*101127*1719*U*00400*000003438*0*P*>
        GS*GF*4405197800*999999999*20111219*1742*000000003*X*004010
        ST*990*000000003
        B1*XXXX*9999919860*20111218*A
        N9*CN*9999919860
        SE*4*000000003
        GE*1*000000003
        IEA*1*000000003""")
        ftp.storbinary('STOR ' + filename+".edi", output)


ediObject = EDI()    
ediObject.main()  
