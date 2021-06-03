import os
import html
import re
import pickle
from lxml import etree
from lxml import etree as ET2
#import xml.etree.ElementTree as ET
import spacy
nlp = spacy.load("en_core_web_sm")
lemmatizer = nlp.get_pipe("lemmatizer")

regard_ent_type = ['LANGUAGE','DATE', 'TIME','MONEY','QUANTITY', 'ORDINAL', 'CARDINAL']
# Tokenize and lemmatize the sentence, while keeping the name entity phrase as an item
def tokenizer(sentence):
    doc = nlp(sentence)
    entities_atr = {}
    entities_phrase_dic = {}
    for ent in doc.ents:
        if ent.label_ not in regard_ent_type: 
            entities_atr[ent.text] = ent.label_
            if ' ' in ent.text:
                entities_phrase_dic[ent.text] = 0

    org_tokens_list = []
    for token in doc:
        org_tokens_list.append(token.text)
    #print(org_tokens_list)

    for index in range(len(org_tokens_list)):
        for name in entities_phrase_dic:
            if ' ' in name:
                name_list = name.split(' ')
            else:
                name_list = [name]
            if org_tokens_list[index:index+len(name_list)] == name_list:
                #print(org_tokens_list[index:index+len(name_list)])
                #print(name_list)
                entities_phrase_dic[name] = (index, index + len(name_list))
    #print(entities_dic)

    with doc.retokenize() as retokenizer:
        for name in entities_phrase_dic:
            if entities_phrase_dic[name] != 0:
                spans = doc[entities_phrase_dic[name][0]:entities_phrase_dic[name][1]]
                #filtered = spacy.util.filter_spans(spans)
                try:
                    retokenizer.merge(spans, attrs={"LEMMA": name.lower()})
                except ValueError:
                    pass

    new_tokens_list = []
    for token in doc:
        if token.pos_ != 'SPACE':
            new_tokens_list.append(token.lemma_.lower()) # or token.text
    #print(new_tokens_list)

    return new_tokens_list #, entities_atr


# Pack each instance(a instance = a blog) into a class object
class GroupData:
    def __init__(self, blog_id, user_id, gender, age, industry, astrology, date, post):
        self.blog_id = blog_id
        self.user_id = user_id
        self.gender = gender
        self.age = age
        self.industry = industry
        self.astrology = astrology
        self.date = date
        self.post = post


# Get file name list from corpus blogs
def get_filename(filepath):
    filename_list = os.listdir(filepath)
    # Return a list of file name
    return filename_list


# Deconstruct the xml file
# Compose each instance based on the filename and content 
# Package it into a class object and add it to a list
def get_one_file(filepath, filename, index):
    data_list = []
    text = ''
    with open(filepath+filename, 'r', encoding='ISO-8859-1') as f:
        try:
            for line in f:
                line = html.unescape(line)
                text += line
        except UnicodeDecodeError:
            print('Error 1', filename)
        
    #print(text)
    #root = ET.fromstring(text)
    parser = ET2.XMLParser(recover=True)
    try:
        root = ET2.fromstring(text, parser=parser)
        #root = tree.getroot()

        info = filename.split('.')
        user_id = info[0]
        gender = info[1]
        age = info[2]
        industry = info[3]
        astrology = info[4]

        for child in root:
            blog_id = index
            if child.tag == 'date':
                date = child.text 
            elif child.tag == 'post':
                data_sample = GroupData(blog_id, user_id, gender, age, industry, astrology, date, child.text.strip('\n \t'))
                data_list.append(data_sample)
                index += 1
    except etree.XMLSyntaxError:
        print('Error 2', filename)

    return data_list, index


def get_data(filepath, index):
    # Get a data list
    data_lists = []
    filename_list = get_filename(filepath)
    
    for filename in filename_list:
        #clean_data(filepath, filename)
        data_list, index = get_one_file(filepath, filename, index)
        data_lists += data_list

    # Store the data(class object) list into a pickle file
    with open('./group_data_objects.pickle','wb') as p:
        pickle.dump(data_lists, p)

    return data_lists

    


if __name__ == '__main__':
    filepath = '/Users/tan/OneDrive - xiaozhubaoxian/blog/blogs/'
    index = 0
    #get_data(filepath, index)
    
    # Read a pickle file
    with open('./group_data_objects.pickle', 'rb') as f:
        data_lists = pickle.load(f)

    # Print examples
    for i in data_lists[:3]:
        #print(i.blog_id, i.user_id, i.gender, i.age, i.industry, i.astrology, i.date, i.post, '\n')
        print(tokenizer(i.post))
    
    
    



'''
# test html and xml parser
filepath = '/Users/tan/OneDrive - xiaozhubaoxian/blog/blogs/'
filename = '467705.female.25.indUnk.Libra.xml'
text = ''
p5 = re.compile('(&nbsp;| {2,}|�|Ã|Â|ï|¿|½|¯|¢)')
with open(filepath+filename, 'r', encoding='ISO-8859-1') as f:
    for line in f:
        line = html.unescape(line)
        #line = p5.sub('', line)
        text += line

    #print(text)
    #root = ET.fromstring(text)
    parser = ET2.XMLParser(recover=True)
    root = ET2.fromstring(text, parser=parser)
    for child in root[:4]:
        print(child.tag, child.text), '\n\n'
'''

'''
# test re
text = "i was waiting for my DESTINY.what should i do with myself,tell me o' my heartwhat should i do with myself,tell me....should i fly, with this beautiful nature.or should i play with these winds.should i try to reach the skies,or should i pray to the mother earth.what should i do with myself friendstell me....she talked in such a way,gave me dreams with thousand colours.like i stand in the middle of island,and she shows me all the love she has,my first dream , "
p2 = re.compile('( \, )|(\,(?=[a-zA-Z]))')
p3 = re.compile('( \. )|(\.(?=[a-zA-Z]))')
text = p2.sub(', ', text)
text = p3.sub('. ', text)
print(text)'''
