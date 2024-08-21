import praw
import configparser
import pandas as pd
import time
from random import randint

def setup_reddit():
    config = configparser.ConfigParser()
    config.read('praworiginal.ini')
    client_id = config['DEFAULT']['client_id']
    client_secret = config['DEFAULT']['client_secret']
    user_agent = config['DEFAULT']['user_agent']
    return praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

def scrape_questions(subreddit_name, total_questions=1000):
    reddit = setup_reddit()
    subreddit = reddit.subreddit(subreddit_name)
    questions = []
    count = 0
    after = None
    seen_ids = set()

    while count < total_questions:
        submissions = list(subreddit.new(limit=100, params={'after': after}))
        for submission in submissions:

            if submission.id in seen_ids:
                submission_date = pd.to_datetime(submission.created_utc, unit= 's')
                print(f"Duplicate submission found with ID {submission.id}. Submission date: {submission_date}")
                return questions  # Beende die Funktion, um die Schleife zu unterbrechen
            
            seen_ids.add(submission.id)  # ID zur Menge der gesehenen IDs hinzufügen

            if submission.title.endswith('?'):
                question = {
                    'title': submission.title,
                    'text': submission.selftext,
                    'timestamp': pd.to_datetime(submission.created_utc, unit='s')
                }
                questions.append(question)
                count += 1
                print(count)
                if count >= total_questions:
                    break
        after = submissions[-1].fullname if submissions else None
        time.sleep(randint(1, 3))  # Verzögerung zwischen den API-Aufrufen

    print(f"Scraped {len(questions)} questions.")
    for question in questions:
        print(question)  # Ausgabe jeder Frage zur Überprüfung
    return questions

if __name__ == '__main__':
    questions = scrape_questions('nutrition')  # Ändere 'diet' zu 'nutrition'
    if questions:
        df = pd.DataFrame(questions)
        df.to_csv('reddit_nutrition_questions.csv', index=False)  # Ändere den Dateinamen entsprechend
        print('File reddit_nutrition_questions.csv created successfully.')
    else:
        print('No questions were scraped.')