from flask import Flask,render_template,request
from py2neo import Node, Relationship, Graph, NodeMatcher
import json
import time

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/sql",methods=['GET','POST'])
def sql():

    class treeNode:
        def __init__(self, nameValue):
            self.name = nameValue
            self.children = {}
            self.isEnd = 0
        def disp(self, ind=1):
            with open("display.txt",encoding="utf-8",mode="a") as f:
                f.write(' '*(ind) + str(self.name) + str(self.isEnd) + ' ' + "\n")
            for child in self.children.values():
                child.disp(ind+1)

    def updateTokenTree(items, inTree):
        if items[0] not in inTree.children:
            inTree.children[items[0]] = treeNode(items[0])
            if len(items) == 1 :
                inTree.children[items[0]].isEnd = 1
        if len(items) == 1 and items[0] in inTree.children:
            inTree.children[items[0]].isEnd = 1
        if len(items) > 1:
            updateTokenTree(items[1::], inTree.children[items[0]])

    def createTokenTree(dataset):
        retTree = treeNode("Null")
        for trans in dataset:
            updateTokenTree(trans, retTree)
        return retTree

    def LoadData(DictFile):
        with open(DictFile,mode="r",encoding="utf-8") as file:
            test_data = []
            for line in file:
                test_data.append(line.strip().encode('utf-8').decode('utf-8-sig'))
        data = list(map(list,test_data))
        return data

    def mineTree(TokenTree, sentence, a, EndFlag = 0):
        EndFlag = TokenTree.isEnd
        if a <= (len(sentence) - 1):
            if sentence[a] in TokenTree.children:
                a = a + 1
                a, EndFlag = mineTree(TokenTree.children[sentence[a-1]], sentence, a, EndFlag)
        return a, EndFlag

    def tokenize(TokenTree,sentence):
        toke=[]
        sentencelen =  len(sentence)
        StartIndex = 0
        Endflag = 0
        while sentencelen != 0:
            a = 0
            a, Endflag = mineTree(TokenTree, sentence, a)
            if a == 0 :
                sentence = sentence[1:len(sentence)]
                sentencelen = len(sentence)
                StartIndex += 1
            elif a == 1 :
                if Endflag:
                    toke.append([sentence[0:a],StartIndex,StartIndex+a-1])
                    StartIndex += a
                    sentence = sentence[a:len(sentence)]
                    sentencelen = len(sentence)
                else :
                    StartIndex += a
                    sentence = sentence[a:len(sentence)]
                    sentencelen = len(sentence)
            else :
                if Endflag:
                    toke.append([sentence[0:a],StartIndex,StartIndex+a-1])
                    StartIndex += a
                    sentence = sentence[a:len(sentence)]
                    sentencelen = len(sentence)
                else :
                    StartIndex += a
                    sentence = sentence[a:len(sentence)]
                    sentencelen = len(sentence)
        return toke
    
    Tag = "tag_dictionary.txt"
    Director = "director.txt"
    Actor = "actor.txt"
    # emotion dictionary
    Happy = "happy.txt"
    Sad = "sad.txt"
    Terrible = "terrible.txt"
    Inspire = "inspire.txt"

    Tag_Data = LoadData(Tag)
    Director_Data = LoadData(Director)
    Actor_Data = LoadData(Actor)
    Happy_Data = LoadData(Happy)
    Sad_Data = LoadData(Sad)
    Terrible_Data = LoadData(Terrible)
    Inspire_Data = LoadData(Inspire)

    Tag_tree = createTokenTree(Tag_Data)
    Director_tree = createTokenTree(Director_Data)
    Actor_tree = createTokenTree(Actor_Data)
    Happy_tree = createTokenTree(Happy_Data)
    Sad_tree = createTokenTree(Sad_Data)
    Terrible_tree = createTokenTree(Terrible_Data)
    Inspire_tree = createTokenTree(Inspire_Data)

    text_data = request.get_json()
    sentence = text_data["msg"]
    print("-----")
    print(request.method)
    print("-----")

    print("Tag : ")
    Tag_toke = tokenize(Tag_tree, sentence)
    print(Tag_toke)
    print("Director : ")
    Director_toke = tokenize(Director_tree, sentence)
    print(Director_toke)
    print("Actor :")
    Actor_toke = tokenize(Actor_tree, sentence)
    print(Actor_toke)
    print("Happy :")
    Happy_toke = tokenize(Happy_tree, sentence)
    print("Sad :")
    Sad_toke = tokenize(Sad_tree, sentence)
    print("Terrible :")
    Terrible_toke = tokenize(Terrible_tree, sentence)
    print("Inspire :")
    Inspire_toke = tokenize(Inspire_tree, sentence)
    emotion = []

    if len(Happy_toke) + len(Inspire_toke) + len(Sad_toke) + len(Terrible_toke) != 0:
        if len(Happy_toke) + len(Inspire_toke) >= len(Sad_toke) + len(Terrible_toke):
            if len(Happy_toke) > 0:
                emotion.append("Happy")
            if len(Inspire_toke) > 0:
                emotion.append("Inspire")
        else:
            if len(Sad_toke) > 0:
                emotion.append("Sad")
            if len(Terrible_toke) > 0:
                emotion.append("Terrible")
    print(emotion)

    # 請在這裡修改連線資訊
    def tag_token_search(token):
        output_sql_data = {}
        g = Graph("http://140.116.245.151:7474/", auth = ("neo4j", "neo4j"))
        sql_instr = "MATCH p = (n0:tag_type{name:\"" + token[0][0] + "\"})-[:tag]-(n1) RETURN n1"
        data = g.run(sql_instr).data()
        for iter in range(len(data)):
            row_data_list = []
            row_data_list.append(data[iter]["n1"]["name"])
            row_data_list.append(data[iter]["n1"]["IMG"])
            row_data_list.append(data[iter]["n1"]["URL"])
            output_sql_data[data[iter]["n1"]["name"]] = row_data_list
        return output_sql_data

    def director_token_search(token):
        output_sql_data = {}
        g = Graph("http://140.116.245.151:7474/", auth = ("neo4j", "neo4j"))
        sql_instr = "MATCH p = (n0:Director_type{name:\"" + token[0][0] + "\"})-[:Director]-(n1) RETURN n1"
        data = g.run(sql_instr).data()
        for iter in range(len(data)):
            row_data_list = []
            row_data_list.append(data[iter]["n1"]["name"])
            row_data_list.append(data[iter]["n1"]["IMG"])
            row_data_list.append(data[iter]["n1"]["URL"])
            output_sql_data[data[iter]["n1"]["name"]] = row_data_list
        return output_sql_data

    def actor_token_search(token):
        output_sql_data = {}
        g = Graph("http://140.116.245.151:7474/", auth = ("neo4j", "neo4j"))
        sql_instr = "MATCH p = (n0:Actor_type{name:\"" + token[0][0] + "\"})-[:actor]-(n1) RETURN n1"
        data = g.run(sql_instr).data()
        for iter in range(len(data)):
            row_data_list = []
            row_data_list.append(data[iter]["n1"]["name"])
            row_data_list.append(data[iter]["n1"]["IMG"])
            row_data_list.append(data[iter]["n1"]["URL"])
            output_sql_data[data[iter]["n1"]["name"]] = row_data_list
        return output_sql_data

    def emotion_token_search(emotion):
        output_sql_data = {}
        g = Graph("http://140.116.245.151:7474/", auth = ("neo4j", "neo4j"))
        sql_instr = ""
        if len(emotion) == 1:
            sql_instr = "MATCH p = (n0:Emotion_type{name:\"" + emotion[0] + "\"})-[:emotion]-(n1) RETURN n1"
        elif len(emotion) == 2:
            sql_instr = "MATCH p = (n0:Emotion_type{name:\"" + emotion[0] + "\"})-[:emotion]-(n1)-[:emotion]-(n2:Emotion_type{name:\""+ emotion[1] +"\"}) RETURN n1"
        data = g.run(sql_instr).data()
        for iter in range(len(data)):
            row_data_list = []
            row_data_list.append(data[iter]["n1"]["name"])
            row_data_list.append(data[iter]["n1"]["IMG"])
            row_data_list.append(data[iter]["n1"]["URL"])
            output_sql_data[data[iter]["n1"]["name"]] = row_data_list
        return output_sql_data


    try:
        # 限制 output_data 的 length
        def limit_max_length(output_data):
            output_max_length = 10
            if len(output_data) > output_max_length:
                temp_output_data = {}
                for item in output_data:
                    if len(temp_output_data) < output_max_length:
                        temp_output_data[item] = output_data[item]
                output_data = temp_output_data
            return output_data

        descriptions = ["名稱"]
        output_sql_data = {}
        tag_output_data = {}
        director_output_data = {}
        actor_output_data = {}
        emotion_output_data = {}
        director_emotion_output_data = {}
        actor_emotion_output_data = {}

        if len(Tag_toke) > 0:
            tag_output_data = tag_token_search(Tag_toke)
        if len(Director_toke) > 0:
            director_output_data = director_token_search(Director_toke)
        if len(Actor_toke) > 0:
            actor_output_data = actor_token_search(Actor_toke)
        if len(emotion) > 0:
            emotion_output_data = emotion_token_search(emotion)

        # director and emotion
        director_and_emotion = director_output_data.keys() & emotion_output_data.keys()
        for item in director_and_emotion:
            if item in director_output_data:
                director_emotion_output_data[item] = director_output_data[item]

        # actor and emotion
        actor_and_emotion = actor_output_data.keys() & emotion_output_data.keys()
        for item in actor_and_emotion:
            if item in actor_output_data:
                actor_emotion_output_data[item] = actor_output_data[item]

        tag_output_data = limit_max_length(tag_output_data)
        director_output_data = limit_max_length(director_output_data)
        actor_output_data = limit_max_length(actor_output_data)
        emotion_output_data = limit_max_length(emotion_output_data)
        director_emotion_output_data = limit_max_length(director_emotion_output_data)
        actor_emotion_output_data = limit_max_length(actor_emotion_output_data)

        response = {
            "descriptions": descriptions,
            "rows": output_sql_data,
            "tag_rows": tag_output_data,
            "director_rows": director_output_data,
            "actor_rows": actor_output_data,
            "emotion_rows": emotion_output_data,
            "director_emotion_rows": director_emotion_output_data,
            "actor_emotion_rows": actor_emotion_output_data
        }
    except:
        response = {"descriptions": ["指令打錯了"], "rows": [["回去重寫"]]}
    try:
        return json.dumps(response)
    except:
        response = {"descriptions": ["指令打錯了"], "rows": [["回去重寫"]]}
        return json.dumps(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000',debug=True)