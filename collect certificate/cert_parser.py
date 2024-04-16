# -*- coding: utf-8 -*-

from OpenSSL import crypto
from datetime import datetime
import pandas as pd
import os

class Cert_Parser:

    extension = {}

    f1 = {}     # basic_fields_features
    f2 = {}     # computed_features
    f3 = {}     # exist_info_features
    f4 = {}     # critical_info_features
    f5 = {}     # RFC_5280_check_features
    f6 = {}     # cert_chain_features

    def parse_pem_cert(self, pem_cert):
        try:
            self.cert = crypto.load_certificate(crypto.FILETYPE_PEM, str.encode(pem_cert))
            # self.cert = x509.load_pem_x509_certificate(pem_cert)
            self.issuer = self.cert.get_issuer()
            self.subject = self.cert.get_subject()
        except Exception as e:
            print(e)


    def extract_basic_features(self):
        # basic fields
        self.f1['issuer_country'] = self.issuer.countryName
        self.f1['subject_country'] = self.subject.countryName
        self.f1['version'] = self.cert.get_version()
        self.f1['sign_algorithm'] = self.cert.get_signature_algorithm().decode('utf-8')


    def extract_computed_features(self):
        # computed from basic fields
        self.f2['serial_number_length'] = self.cert.get_serial_number().bit_length()
        self.f2['has_expired'] = True if self.cert.has_expired() else False
        self.f2['issuer_is_empty'] = False if self.issuer else True
        self.f2['issuer_cn_exist'] = True if self.issuer.commonName else False
        self.f2['subject_is_empty'] = False if self.subject else True
        self.f2['subject_cn_exist'] = True if self.subject.commonName else False
        self.f2['no_extension'] = False if self.cert.get_extension_count() else True
        self.f2['public_key_size'] = self.cert.get_pubkey().bits()
        
        # validation
        valid_from = datetime.strptime(self.cert.get_notBefore().decode('ascii'),'%Y%m%d%H%M%SZ')
        valid_till = datetime.strptime(self.cert.get_notAfter().decode('ascii'),'%Y%m%d%H%M%SZ')
        now = datetime.now()
        self.f2['valid_time_length'] = (valid_till - valid_from).days
        self.f2['valid_time_so_far'] = (now - valid_from).days


    def extract_extension_features(self):
        ''' 
        exist info & critical info, including:
        keyUsage, authorityInfoAccess, certificatePolicies, basicConstraints,cRLDistributionPoints,
        subjectAltName, extendedKeyUsage, subjectKeyIdentifier, signedCertificateTimestampList, 
        inhibitAnyPolicy, policyConstraints, nameConstraints, issuerAlternativeName
        '''
        ext_count = self.cert.get_extension_count()
        for i in range(0, ext_count):
            ext = self.cert.get_extension(i)
            ext_name = str(ext.get_short_name())
            self.f3[ext_name +'_is_exist'] = True
            self.f4[ext_name + '_is_critical'] = ext.get_critical()

            if 'keyUsage' in ext_name:
                ext_content = ext.__str__()
                self.f1['digital_signature'] = True if 'Digital Signature' in ext_content else False
                self.f1['key_encipherment'] = True if 'Key Encipherment' in ext_content else False
                self.f1['data_encipherment'] = True if 'Data Encipherment' in ext_content else False
                self.f1['key_agreement'] = True if 'Key Agreement' in ext_content else False
                self.f1['non_repudiation'] = True if 'Non Repudiation' in ext_content else False
    
    def extract(self):
        self.extract_basic_features()
        self.extract_computed_features()
        self.extract_extension_features()
        self.feature_dict = self.f1 | self.f2 | self.f3 | self.f4



   

if __name__ == '__main__':
    PATH = os.getcwd() + '/legal certificates'

    data = []
    for root, dirs, files in os.walk(PATH):
        for file in files:
            with open(os.path.join(root, file), 'r')as f:
                pem_cert = f.read()
                
                parser = Cert_Parser()
                parser.parse_pem_cert(pem_cert)
                parser.extract()
                data.append(parser.feature_dict)

    pd.DataFrame(data).to_csv('out.csv', header = True, index = True, sep = ",")