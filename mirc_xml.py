import argparse
import csv
import glob
import logging
import os
import re
import xml.etree.ElementTree as etree
import zipfile

def get_xml_root(xmlstring):
    return etree.fromstring(xmlstring)

def has_siuid(root):
    if root.find("./phi/study/si-uid") is not None:
        return True
    return False

def sectionstr(root, section):
    sectel = root.find('./section[@heading="{}"]'.format(section))
    if sectel is None:
        return ""
    outstr = "".join(sectel.itertext())
    outstr = outstr.replace("\r", " ")
    outstr = outstr.replace("\n", " ")
    # replace multiple spaces with one space
    outstr = re.sub(r"\ {2,}", " ", outstr)
    return outstr.strip()
    
def output_row(root, filename):
    # authors
    authors = root.findall("./author")
    authorstring = ""
    for a in authors:
        authorstring += "{}/".format(a.find("./name").text)
    authorstring = authorstring[:-1]

    # accession number
    accession = root.find("./phi/study/si-uid").text

    # title
    title = root.find("./title").text

    # history
    history = sectionstr(root, "History")

    # findings
    findings = sectionstr(root, "Findings")

    # diagnosis
    diagnosis = sectionstr(root, "Diagnosis")

    # discussion
    discussion = sectionstr(root, "Discusssion")

    # create and write row
    row = [authorstring, accession, title, history, findings, diagnosis, 
        discussion]
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def write_first_row(filename):
    headers = ['Author', 'Accession', 'Title', 'History', 'Findings', 
        'Diagnosis', 'Discussion']
    with open(filename, 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

def main(args):
    # base directory contains a bunch of zipped files
    zips = glob.glob(os.path.join(args.base_directory,'*'))
    write_first_row(args.outfile)
    folderRegEx = re.compile(r'_([0-9\.]*)\.zip$')
    for z in zips:
        mo = folderRegEx.search(z)
        folder = mo.group(1)
        # read zip
        with zipfile.ZipFile(z, 'r') as zip_ref:
            contents = zip_ref.read(folder + '/MIRCdocument.xml')
            root = get_xml_root(contents)
            if has_siuid(root):
                output_row(root, args.outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("base_directory")
    parser.add_argument("--outfile", default = "cases.csv")
    args = parser.parse_args()
    main(args)