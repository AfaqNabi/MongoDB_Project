import statistics
from bson.objectid import ObjectId
import pymongo
import datetime
import sys

portNumber = int(input("Enter the port number: "))  # get port number from input
connection = pymongo.MongoClient("localhost",
                                 portNumber)  # connect to to local host using portnumber (might need to change)
database = connection['291db']
Posts = database['Posts']
Votes = database['Votes']
Tags = database['Tags']
invalid_input = "Invalid Input Try Again"

invalid_char_array = [8, 9, 11, 32, 0, 27, 10, 13]  # if user enters any tabs, spaces etc
nothing = ['']  # if user enters nothing
padding = '-------+------------+--------------------------------+--------------------------' \
          '------+--------+----------------------+------------+--------------+'


def main():
    # successfully entered the main function and entered the database
    # counters/ids for the below fields
    question_Id = 0
    votes_Id = 0
    answers_Id = 0
    tags_Id = 0
    Posts.create_index([("Id", 1)])
    print("Database connected")  # print if connection successfull
    print("MongoDB MINI-PROJECT 2\nAfaq Nabi\nNatnail Ghebresilasie\nKrutik Soni\n")
    # default to UID=NONE
    UID = None  # might need to change this#########
    program_exit = False
    keywords = []
    done = False
    counter = 0
    while not program_exit:
        # allow user to choose if they want to login or not
        login = input("Would you like to enter a UID? (Y/N) or exit the program(E): ")
        while login.lower() not in ['y', 'n', 'e']:
            print(invalid_input)
            login = input("Would you like to enter a UID? (Y/N) or exit the program(E): ")

        # if they choose to exit then exit
        if login.lower() == 'e':
            sys.exit()

        # assign a userID and show all the information related to the user if they entered a uid
        elif login.lower() == 'y':
            UID = user_ID()
            numberOfQuestions, averageQScorecore = questions(UID)
            numberOfAnswers, averageAScore = answers(UID)
            numberOfVotes = votes(UID)
            print("Number of Questions: ", numberOfQuestions)
            print("Avg Question Score: ", averageQScorecore)
            print("# of Answers: ", numberOfAnswers)
            print("Avg Score: ", averageAScore)
            print("# of Votes: ", numberOfVotes)
        # boolean for returning to the main menue

        main_menu = False
        # loop while user does not choose to return to the main menu
        while not main_menu:
            # give user option to post search or exit
            action = input("Would you like to post a question(P) or Search for a Question(S) or Exit(E): ")
            while action.lower() not in ["p", 's', 'e']:
                print(invalid_input)
                action = input("Would you like to post a question(P) or Search for a Question(S) or Exit(E): ")

            if action.lower() == 'e':
                main_menu = True
                sys.exit()

            elif action.lower() == 'p':
                question_Id, tags_Id = post_question(question_Id, tags_Id, UID)

            # loop for search action
            elif action.lower() == 's':
                question_Id, votes_Id, answers_Id, tags_Id = main_search(UID, question_Id, votes_Id, answers_Id,
                                                                         tags_Id)


def main_search(UID, question_Id, votes_Id, answers_Id, tags_Id):
    keywords = input("Enter 1 or more keywords separated by a space to search for a question: ")
    while keywords in nothing or ord(keywords[0]) in invalid_char_array:
        print(invalid_input)
        keywords = input("Enter 1 or more keywords separated by a space to search for a question: ")

    words = keywords.split()
    useThisArray = []
    resultsFromSearch = searchQuestion(words)
    for objects in resultsFromSearch:
        for key, value in objects.items():
            if key != '_id':
                print("{}: {}".format(key, value, ))
                useThisArray.append(objects)
        print("\n")

    post_action = input("Pick a question(P) or Back to Main Menu(M): ")
    while post_action.lower() not in ['p', 'm']:
        print(invalid_input)
        post_action = input("Pick a question(P) or Back to Main Menu(M): ")

    if post_action.lower() == 'm':
        return question_Id, votes_Id, answers_Id, tags_Id
    else:
        question_Id, votes_Id, answers_Id, tags_Id = pickQ(UID, useThisArray, question_Id, votes_Id, answers_Id,
                                                           tags_Id)
        return question_Id, votes_Id, answers_Id, tags_Id


def pickQ(UID, useThisArray, question_Id, votes_Id, answers_Id, tags_Id):
    pick_question = input(
        "Enter the ID of the displayed questions to pick one: ")  # post id that is used to search for all answers of that question
    while pick_question in nothing or ord(pick_question[0]) in invalid_char_array or pick_question.isalpha():
        print(invalid_input)
        pick_question = input(
            "Enter the ID of the displayed questions to pick one: ")  # post id that is used to search for all answers of that question

    picked = None
    valid_picked_id = False
    while not valid_picked_id:
        for post in useThisArray:
            if pick_question == post['Id']:
                picked = display_picked_post(post['_id'])
                break
        if not picked:
            print("The entered Id is not in the printed Questions")
            pick_question = input(
                "Enter the ID of the displayed questions to pick one: ")  # post id that is used to search for all answers of that question
            while pick_question in nothing or ord(pick_question[0]) in invalid_char_array or pick_question.isalpha():
                print(invalid_input)
                pick_question = input(
                    "Enter the ID of the displayed questions to pick one: ")  # post id that is used to search for all answers of that question
        else:
            valid_picked_id = True

    print('\nTHE QUESTION')
    for key, val in picked[0].items():
        if key == "Body":
            print("{}: {:.80}".format(key, val))
        else:
            print("{}: {}".format(key, val))
    print('\n', "-" * 100)
    # gets array of all answers

    all_answers_array, if_accepted_answer = actionList(pick_question)

    if if_accepted_answer == True:
        print("*")

    # print this if there are no answers
    if len(all_answers_array) == 0:
        print("Question has zero answers")

    # if there is an accepted answer print it this way
    else:
        print("Answers to the Picked Question")
        for dicts in all_answers_array:
            for key, value in dicts.items():
                if key == "Body":
                    print("{}: {:.80}".format(key, value))
                elif key != "_id":
                    print("{}: {}".format(key, value))
            print('\n')

    # actions to answer a question, pick an answer or vote
    answer_or_pick = input(
        "Answer the question(A), Pick an answer from the displayed answers(P) or Vote on the picked question(V): ")
    while answer_or_pick.lower() not in ['a', 'p', 'v']:
        print(invalid_input)
        answer_or_pick = input(
            "Answer the question(A), Pick an answer from the displayed answers(P) or Vote on the picked question(V): ")

    # answer the question
    if answer_or_pick.lower() == 'a':
        answers_Id = actionAnswer(UID, pick_question, answers_Id)

    # vote on the question that was picked
    elif answer_or_pick.lower() == 'v':
        votes_Id = actionVote(pick_question, UID, votes_Id)

    # pick an answer from the risplayed answers
    else:
        pick_answer(UID, all_answers_array, votes_Id)
    return question_Id, votes_Id, answers_Id, tags_Id


def pick_answer(UID, all_answers_array, votes_Id):
    pick_answer = input("Enter the ID of the displayed answers to pick one: ")

    while pick_answer in nothing or ord(pick_answer[0]) in invalid_char_array or pick_answer.isalpha():
        print(invalid_input)
        pick_answer = input("Enter the ID of the displayed answers to pick one: ")
    answer_returned = []

    truth_v = False
    while not truth_v:
        for answers_to_questions in all_answers_array:
            if answers_to_questions['Id'] == str(pick_answer):
                answer_returned = display_picked_post(answers_to_questions['_id'])
        if not answer_returned:
            print("The entered Id is not in the printed answers try again")
            pick_answer = input("Enter the ID of the displayed answers to pick one: ")
            while pick_answer in nothing or ord(pick_answer[0]) in invalid_char_array or pick_answer.isalpha():
                print(invalid_input)
                pick_answer = input("Enter the ID of the displayed answers to pick one: ")
        else:
            truth_v = True

    for key, val in answer_returned[0].items():
        if key == "Body":
            print("{}: {:.80}".format(key, val))
        else:
            print("{}: {}".format(key, val))

    vote_on_answer = input("You may vote on this answer(V) or go Back to Main Menu(M): ")
    while vote_on_answer.lower() not in ['m', 'v']:
        print(invalid_input)
        vote_on_answer = input("You may vote on this answer(V) or go Back to Main Menu(M): ")
    if vote_on_answer.lower() == 'v':
        votes_Id = actionVote(pick_answer, UID, votes_Id)

    return votes_Id


def display_picked_post(object_id):
    returnArray = []
    newViewCount = None
    question = False
    checkThePost = Posts.find({'_id': ObjectId(object_id)}, {"PostTypeId": 1})
    for obj in checkThePost:
        if obj["PostTypeId"] == "1":
            question = True

    if question == True:
        find_post = Posts.find({'_id': ObjectId(object_id)}, {"ViewCount": 1})
        for obj in find_post:
            newViewCount = obj["ViewCount"] + 1
            Posts.update_one({"_id": ObjectId(object_id)}, {"$set": {"ViewCount": newViewCount}})

    find_post = Posts.find({'_id': ObjectId(object_id)})

    for obj in find_post:
        returnArray.append(obj)

    return returnArray


def post_question(question_Id, tags_Id, UID=None):
    title = input("Enter the title for your question: ")
    body = input("Enter the body for your question: ")
    currentDate = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S:%f")
    tagsArrayAfter = []
    tagsArrayBefore = []
    done = False
    while not done:
        # append the tags into one array without the arrows < and >
        # append the tags into another array with the arrows for proper formatting
        tag = input("Enter the tag: ")
        while tag in nothing or ord(tag[0]) in invalid_char_array:
            print(invalid_input)
            tag = input("Enter the tag: ")

        tagsArrayBefore.append(tag)
        tag = "<" + tag + ">"
        tagsArrayAfter.append(tag)

        yesOrNo = input("Would you like to add more tags? (Y/N): ").lower()
        while yesOrNo.lower() not in ['y', 'n']:
            yesOrNo = input("Would you like to add more tags? (Y/N): ")

        done = yesOrNo.lower() in ['n']
    question_Id = 1 + question_Id
    postID = str(question_Id) + "q"
    # postID = str(postID)
    tagsInString = ""
    for i in tagsArrayAfter:
        tagsInString += i

    if UID == None:
        qpost = {"Id": postID, "PostTypeId": "1", "CreationDate": currentDate, "Score": 0, "ViewCount": 0, "Body": body,
                 "Title": title, "Tags": tagsInString, "AnswerCount": 0, "CommentCount": 0, "FavoriteCount": 0}
    else:
        qpost = {"Id": postID, "PostTypeId": "1", "CreationDate": currentDate, "Score": 0, "ViewCount": 0, "Body": body,
                 "OwnerUserId": UID, "Title": title, "Tags": tagsInString, "AnswerCount": 0, "CommentCount": 0,
                 "FavoriteCount": 0,
                 "ContentLicense": "CC BY-SA 2.5"}

    Posts.insert_one(qpost)

    # for every tag go into tags document and count and store new count
    # tagsArrayBefore is so that you can find the tags without them having the < and > in them
    for i in tagsArrayBefore:
        # x is 1 if the tag exists already in Tags collection, x is 0 if it doesn't exist then we make a new tag in Tags
        x = Tags.count_documents({"TagName": i})
        if x != 0:
            print(str(i), ": This tag exists already")
            foundTag = Tags.find({"TagName": i})
            for j in foundTag:
                tagCount = 1 + j["Count"]
                Tags.update_one({"TagName": i}, {"$set": {"Count": tagCount}})
        # orelse add new tag
        else:
            tagID = str(tags_Id) + "t"
            tagToInsert = {"Id": tagID, "TagName": i, "Count": 1}
            Tags.insert_one(tagToInsert)
        tags_Id = 1 + tags_Id

    return question_Id, tags_Id


def user_ID():
    UID = input("Enter your UID: ")
    while UID in nothing or ord(UID[0]) in invalid_char_array:
        print(invalid_input)
        UID = input("Enter your UID: ")
    return UID


def questions(UID):
    scores = []

    num_q = Posts.find({"OwnerUserId": UID, "PostTypeId": "1"})
    numberOfQuestions = 0

    # put each questions score into scores array
    for question in num_q:
        scores.append(int(question['Score']))
        numberOfQuestions += 1

    # get mean the average score of the persons questions
    try:
        avg_score = statistics.mean(scores)
    except Exception as StatisticsError:
        avg_score = 0
    return numberOfQuestions, avg_score


def answers(UID):
    scores = []
    num_a = Posts.find({"OwnerUserId": UID, "PostTypeId": "2"})
    count_answers = 0

    for answer in num_a:
        scores.append(int(answer['Score']))
        count_answers += 1

    try:
        avg_score = statistics.mean(scores)
    except Exception:
        avg_score = 0
    return count_answers, avg_score


def votes(UID):
    num_v = Votes.find({"UserId": UID})
    numberOfVotes = 0
    for vote in num_v:
        numberOfVotes += 1
    return numberOfVotes


def searchQuestion(keyword_list):
    # use this to get the results for each keyword, then append the results into a list outside of this function,
    # where you called it
    # use terms to search for keyword in posts title and body if length of the word is >= to 3
    # otherwise go through the post and title to find the result
    # search the tags field of the posts regardless if length is >= to 3
    # FIX DUPLICATES, YOU WILL GET DUPLICATES IF A POST HAS A TERM AND TAG THAT ARE THE SAME KEYWORD!!!!
    returnArray = []
    for keyword in keyword_list:
        if len(keyword) >= 3:
            termSearch = Posts.find({"$and": [{"terms": keyword.lower()}, {"PostTypeId": "1"}]},
                                    {"_Id": 1, "Id": 1, "Title": 1, "CreationDate": 1, "Score": 1, "AnswerCount": 1})
            tagSearch = Posts.find({"$and": [{"Tags": {"$regex": "<" + keyword.lower() + ">"}}, {"PostTypeId": "1"}]},
                                   {"_Id": 1, "Id": 1, "Title": 1, "CreationDate": 1, "Score": 1, "AnswerCount": 1})
            for objects in termSearch:
                if objects not in returnArray:
                    returnArray.append(objects)

            for objects in tagSearch:
                append = True
                for items in returnArray:
                    if objects == items:
                        append = False
                if append:
                    returnArray.append(objects)
        else:
            titleSearch = Posts.find({"$and": [{"Title": {"$regex": keyword}}, {"PostTypeId": "1"}]},
                                     {"_Id": 1, "Id": 1, "Title": 1, "CreationDate": 1, "Score": 1, "AnswerCount": 1})
            bodySearch = Posts.find({"$and": [{"Body": {"$regex": keyword}}, {"PostTypeId": "1"}]},
                                    {"_Id": 1, "Id": 1, "Title": 1, "CreationDate": 1, "Score": 1, "AnswerCount": 1})
            for objects in titleSearch:
                returnArray.append(objects)
            for objects in bodySearch:
                append = True
                for items in returnArray:
                    if objects == items:
                        append = False
                if append:
                    returnArray.append(objects)
            tagSearch = Posts.find({"$and": [{"Tags": {"$regex": "<" + keyword.lower() + ">"}}, {"PostTypeId": "1"}]},
                                   {"_Id": 1, "Id": 1, "Title": 1, "CreationDate": 1, "Score": 1, "AnswerCount": 1})
            for objects in tagSearch:
                append = True
                for items in returnArray:
                    if objects == items:
                        append = False
                returnArray.append(objects)
    return returnArray


def actionAnswer(UID, postID, answers_Id):
    body = input("Enter the body of the answer: ")
    currentDate = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S:%f")
    answers_Id = 1 + answers_Id
    uniqueID = str(answers_Id) + "a"
    if UID == None:
        apost = {"Id": uniqueID, "PostTypeId": "2", "ParentId": postID, "CreationDate": currentDate, "Score": 0,
                 "Body": body, "commentCount": 0, "ContentLicense": "CC BY-SA 2.5"}
    else:
        apost = {"Id": uniqueID, "PostTypeId": "2", "ParentId": postID, "CreationDate": currentDate, "Score": 0,
                 "Body": body, "OwnerUserId": UID, "commentCount": 0, "ContentLicense": "CC BY  -SA 2.5"}
    Posts.insert_one(apost)
    num_answer = Posts.find({"Id": postID}, {"AnswerCount": 1})
    for obj in num_answer:
        count = obj["AnswerCount"] + 1
        Posts.update_one({"Id": postID}, {"$set": {"AnswerCount": count}})
    return answers_Id


def actionList(postID):
    # results array to be returned at the end of the function
    results = []
    i = 0
    theAcceptedAnswer = False
    theAnswer = None
    # this is the accepted answer that is contained withing the mongocursor object
    acceptedAnswer = Posts.find({"$and": [{"AcceptedAnswerId": {"$exists": True}}, {"Id": postID}]},
                                {"AcceptedAnswerId": 1})

    # grab the accepted answer id and find the answer from posts and append it into return array
    for obj in acceptedAnswer:
        theAcceptedAnswerID = obj['AcceptedAnswerId']
        theAnswer = Posts.find({"Id": theAcceptedAnswerID}, {"Id": 1, "Body": 1, "CreationDate": 1, "Score": 1})
        for answer in theAnswer:
            theAcceptedAnswer = True
            results.append(answer)

    # find every answer of teh post
    answers = Posts.find({"ParentId": postID}, {"Id": 1, "Body": 1, "CreationDate": 1, "Score": 1})

    # if the answer is the accepted answer fom every answer then dont append since it i salready appended
    # otherwise append it
    for obj in answers:
        append = True
        for item in results:
            if item == obj:
                append = False
        if append == True:
            results.append(obj)
            # return results array and a bool for the accepted answer
    return results, theAcceptedAnswer


def actionVote(postID, UID, votes_Id):
    # pass postID UID and votes and teh votes_id counter used to increment and create new id
    votes_Id = 1 + votes_Id
    voteID = str(votes_Id) + 'v'
    voteTypeID = '2'
    increaseScore = False
    currentDate = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f"))
    i = 0

    # if UID is none save vote with no uid
    if UID != None:
        voted = Votes.find({"$and": [{"UserId": UID}, {"PostId": postID}]})
        for obj in voted:
            i += 1

        # if else to check if you already voted on the curret post
        if i == 0:
            Votes.insert_one(
                {'Id': voteID, 'PostId': postID, 'VoteTypeId': voteTypeID, 'UserId': UID, 'CreationDate': currentDate})
            print('Success!')
            increaseScore = True
        else:
            print('You already voted on this post')

    # otherwise add the UID
    else:
        Votes.insert_one({'Id': voteID, 'PostId': postID, 'VoteTypeId': voteTypeID, 'CreationDate': currentDate})
        print('Success!')
        increaseScore = True

    if increaseScore == True:
        postToUpdate = Posts.find({"Id": postID}, {"Score": 1})
        for obj in postToUpdate:
            score = obj["Score"] + 1
            Posts.update_one({"Id": postID}, {"$set": {"Score": score}})

    return votes_Id


if __name__ == '__main__':
    main()