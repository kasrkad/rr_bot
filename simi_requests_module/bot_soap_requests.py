

REQUEST_FOR_PRODUCER_RELOAD = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
    <soapenv:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
        <wsse:UsernameToken wsu:Id="UsernameToken-50">
            <wsse:Username>{soap_name}</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{soap_pass}</wsse:Password>
        </wsse:UsernameToken>
    </wsse:Security>
</soapenv:Header>
<soapenv:Body>
    <ru:recreateEsuProducer/>
</soapenv:Body>
</soapenv:Envelope>'''


SIMI_GET_DOC_REQUEST = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:user="http://emias.mos.ru/system/v1/userContext/" xmlns:typ="http://emias.mos.ru/simi/simiService/v5/types/" xmlns:v5="http://emias.mos.ru/simi/document/v5/" xmlns:v51="http://emias.mos.ru/simi/core/v5/">
<soap:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
        <wsse:UsernameToken wsu:Id="UsernameToken-50">
            <wsse:Username>{PPAK_SOAP_USER}</wsse:Username>           
        </wsse:UsernameToken>
    </wsse:Security>
    <user:userContext>
        <user:systemName>SIMI</user:systemName>
        <user:userName>simi_support/tg:{tg}</user:userName>
        <user:userRoleId>1</user:userRoleId>
    </user:userContext>
</soap:Header>
<soap:Body>
    <typ:getDocumentRequest>
    <v5:documentId>{id}</v5:documentId>
    <!--Optional:-->
        </typ:getDocumentRequest>
</soap:Body>
</soap:Envelope>"""


SET_ZOOKEEPER_REQUEST = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
<soapenv:Header/>
    <soapenv:Body>
        <ru:setIntercomConsistentCheckEnabled>
            <intercomConsistentCheckEnabled>{state}</intercomConsistentCheckEnabled>
        </ru:setIntercomConsistentCheckEnabled>
    </soapenv:Body>
</soapenv:Envelope>"""


SET_DOCUMENT_ASSOCIATIONS_COUNT_VALIDATOR_REQUEST = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
    <soapenv:Header/>
        <soapenv:Body>
            <ru:setDocumentAssociationsCountValidationEnabled>
                <documentAssociationsCountValidationEnabled>{state}</documentAssociationsCountValidationEnabled>
            </ru:setDocumentAssociationsCountValidationEnabled>
    </soapenv:Body>
</soapenv:Envelope>"""


SET_DEPRECATION_TEMOTRATORY_LOCK = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
    <soapenv:Header/>
        <soapenv:Body>
            <ru:setDeprecationTemporaryLockEnabled>
                <deprecationTemporaryLockEnabled>{state}</deprecationTemporaryLockEnabled>
            </ru:setDeprecationTemporaryLockEnabled>
        </soapenv:Body>
</soapenv:Envelope>"""


GET_ZOOKEEPER_REQUEST = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
    <soapenv:Header/>
    <soapenv:Body>
        <ru:getIntercomConsistentCheckEnabled/>
    </soapenv:Body>
</soapenv:Envelope>"""


GET_DOCUMENT_ASSOCIATIONS_COUNT_VALIDATOR_REQUEST = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
    <soapenv:Header/>
    <soapenv:Body>
        <ru:getDocumentAssociationsCountValidationEnabled/>
    </soapenv:Body>
</soapenv:Envelope>"""


GET_DEPRECATION_TEMOTRATORY_LOCK = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ru="ru.emias.simi.v2.api.diagnostic.v1">
    <soapenv:Header/>
    <soapenv:Body>
        <ru:getDeprecationTemporaryLockEnabled/>
    </soapenv:Body>
</soapenv:Envelope>"""