import logging
_importResolved = False

logger = logging.getLogger(__name__)

try:
    from OpenSSL import crypto, SSL # type: ignore
    _importResolved = True
except ImportError or ModuleNotFoundError:
    logger.warning("Could not import Module: OpenSSL, for ssl support run command \"pip install pyOpenSSL\"")

def ImportResolved():
    return _importResolved

#from https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
#issuer = None means self signed, else use (e.g.) OpenSSL.crypto.X509().from_cryptography(crypto.x509.load_pem_x509_certificate(fileData).get_subject())
def Create(
    emailAddress : str = "emailAddress",
    commonName : str = "commonName",
    countryName : str = "NT",
    localityName : str = "localityName",
    stateOrProvinceName : str = "stateOrProvinceName",
    organizationName : str = "organizationName",
    organizationUnitName : str = "organizationUnitName",
    serialNumber : int = 0,
    validityStartInSeconds : int = 0,
    validityEndInSeconds : int = 100*365*24*60*60,
    cipher : str = None,
    issuer : SSL.X509Name = None,
    keyFile : str = "private.key",
    certFile : str = "selfsigned.crt") -> bool:

    if not _importResolved:
        raise ImportError("Could not import Module: OpenSSL, for ssl support run command \"pip install pyOpenSSL\"")

    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    if issuer == None:
        cert.set_issuer(cert.get_subject())
    else:
        cert.set_issuer(issuer)
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')

    error = False

    try:
        certF = open(certFile, "wt")
        certF.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    except Exception:
        error = True
    finally:
        certF.close()

    try:
        keyF = open(keyFile, "wt")
        if cipher != None and cipher.strip() != "":
            keyF.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
        else:
            keyF.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k, cipher=cipher).decode("utf-8"))
    except Exception:
        error = True
    finally:
        keyF.close()

    return not error