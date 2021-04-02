import re, os, getopt, sys, requests
from bs4 import BeautifulSoup as bs

def minify(text,ftype):
    url =''
    if ftype=='js':
        url = 'https://javascript-minifier.com/raw'
    if ftype=='css' :
        url = 'https://cssminifier.com/raw'
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    data = {'input': text}
    req = requests.post(url, headers=headers, data=data)
    return(req.text)

php_sig = '!!!_php_sig_!!!'
php_elements = []

def php_remove(m):
    php_elements.append(m.group())
    return php_sig

def php_add(m):
    return php_elements.pop(0)

short_opts = "i:o:jch"
long_opts = ["input=","output=","js","css","help","save"]
js = False
css = False
save = False
inpfile = ''
opfile = ''
filetype = 'default'

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
try:
    arguments, values = getopt.getopt(argument_list, short_opts, long_opts)
except getopt.error as err:
    print (str(err))
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in ("-j", "--js"):
        print ("Only JS minified")
        js = True
    elif current_argument in ("-c", "--css"):
        print ("Only CSS minified")
        css = True
    elif current_argument == "--save":
        save = True
    elif current_argument in ("-i", "--input"):
        inpfile = current_value
        ext = inpfile.split('.')[-1]
        if not os.path.isfile(inpfile) or (ext not in ['php','html','asp','js','css','hub']) or len(inpfile)==0:
            print("input file doesn't exist or invalid format")
            sys.exit(0)
        if(ext in ['js','css']):
            filetype = ext
    elif current_argument in ("-o","--output"):
        if not (len(current_value.strip())==0): 
            opfile = current_value
    
if (len(inpfile.split('.'))>2 and inpfile.split('.')[-2]=='min' and len(opfile)==0) or save:
    print('Will be overwritten')
    opfile = inpfile
    
if len(opfile)==0:
    temp = inpfile.split('.')
    temp.insert(-1, 'min')
    opfile = '.'.join(temp)

f = open(inpfile,'r')
cont = f.read()
f.close()

if filetype in ('js','css'):
    #minify js/css
    minified = minify(cont, filetype)
    f = open(opfile,'w+')
    f.write(minified)
    f.close()
    print('minified', filetype)
else:
    if not (js or css):
        js=True
        css=True
        print('Both css and js will be minified')
    temp_cont = re.sub(r'<\?php.*?\?>', php_remove, cont, flags=re.S+re.M)
    soup = bs(temp_cont,'html.parser')
    scripts = soup.findAll('script')
    styles = soup.findAll('style')
    scc=0
    stc=0
    if js:
        for i in scripts:
            if(len(i)>0 and len(i.contents[0].strip())>0):
                i.string = minify(i.contents[0],'js')
                scc+=1
    if css:
        for i in styles:
            if(len(i)>0 and len(i.contents[0].strip())>0):
                i.string = minify(i.contents[0],'css')
                stc+=1
    
    html = re.sub(php_sig, php_add, soup.prettify(formatter="minimal")).replace('?>=""','?>')
    f = open(opfile,'w+')
    f.write(html)
    f.close()
    print("Scripts minified :", scc)
    print("Stylesheets minified :", stc)
