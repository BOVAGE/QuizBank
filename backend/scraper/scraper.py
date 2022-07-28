import json
import pprint
import re

import requests
from bs4 import BeautifulSoup


class SanfoundryScraper:
    def __init__(self, url):
        self.url = url

    def scrape_text_only(self) -> list:
        res = requests.get(self.url)
        content = res.content
        soup = BeautifulSoup(content, "html5lib")
        ec = soup.find("div", class_="entry-content")
        # gather all ads
        ads = ec.find_all("div", id=re.compile("^sf-ads"))
        # gather all collapse spans - view answer button
        vans = ec.find_all("span", class_="collapseomatic")
        #gather all br tags
        brs = ec.find_all("br") 
        # removes all ads
        for ad in ads:
            ad.decompose() 
        # removes all collapse spans - view answer button
        for van in vans:
            van.decompose()
        # removes all br tags
        for br in brs:
            br.decompose()
        ps = ec.find_all('p')[1:]
        questions = []
        # map letter numbering of option to its index in content
        dict_ans_idx = {'a': 1,'b': 2,'c': 3,'d': 4}
        for p in ps:
            try:
                contents = p.contents
                answer = p.find_next_sibling("div", class_="collapseomatic_content")
                ans, exp = answer.contents[:2]
                ans_let = ans.split(':')[1].strip().lower()
                question = contents[0].split('.')[1].lstrip()
                options = contents[1:]
                options.pop() #remove the last newline char in the list
                # remove correct answer
                correct_answer = options.pop(dict_ans_idx[ans_let]-1) 
                correct_answer = correct_answer.split(')',1)[1].lstrip() 
                # make use of maxsplit argument just in case there isanother useful ')'
                incorrect_answers = [option.split(')', 1)[1].lstrip() for option in options if str(option)]
                explanation = exp.replace('Explanation:', '').strip()
            except:
                # print("Invalid format")
                pass
            else:
                quiz = {
                "question": question,
                "incorrect answers": incorrect_answers,
                "correct_answer": correct_answer,
                "explanation": explanation
                }
                questions.append(quiz)
        return questions


def save_to_json_file(questions, file_path):
    with open(f'{file_path}.json', 'w') as file:
        json.dump(questions, file, ensure_ascii=True, indent=4)


if __name__ == "main":
    print("testing")
    s1 = SanfoundryScraper(
        "https://www.sanfoundry.com/biology-questions-answers-mendels-laws-inheritance-1/"
        )
    output = s1.scrape_text_only()
    save_to_json_file(output, "scraper/data/microbiology/genetics")