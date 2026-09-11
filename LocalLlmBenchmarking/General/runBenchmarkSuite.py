import json
import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from localLlmClient import *

def PrepareForYesNoBenchmarking(llmClient):
    llmClient.TalkToLlm('New context.')
    prompt = 'From now on only answer with "yes", "no", "maybe" or "I don\'t know".'
    llmClient.TalkToLlm(prompt)

def RunYesNoQuestions(llmClient, questionsAndAnswers, startTime=None, maxTimeInSeconds=0):
    total = 0
    succeeded = 0
    failed = 0
    stats = {}
    stats['qaDetails'] = {}
    for qa in questionsAndAnswers:
        # Do the timeout check first
        if (not startTime is None) and (maxTimeInSeconds > 0):
            timeDiff = (datetime.now() - startTime).total_seconds()
            if timeDiff > maxTimeInSeconds:
                raise Exception('Timeout')
        qaDetails = {}
        question = qa['question']
        answer = qa['answer']
        #print(question, '=>', answer)
        prompt = 'From now on only answer with "yes", "no" or "don\'t know".'
        question2 = prompt + ' ' + question
        resp = llmClient.TalkToLlm(question2, 'low')
        print(FormatElapsed(startTime), question, answer, '=>', '"'+resp+'"')
        resp = ProcessYesNoAnswer(resp)
        total += 1
        if CheckResponse(answer, resp):
            succeeded += 1
            qaDetails['succeeded'] = True
        else:
            failed += 1
            qaDetails['succeeded'] = False
            print('!!!!!!!!!!!!!')
        stats['qaDetails'][question] = qaDetails
    stats['total'] = total
    stats['succeeded'] = succeeded
    stats['failed'] = failed
    return stats

def ProcessYesNoAnswer(answer):
    answer = answer.rstrip(".*")
    answer = answer.lstrip("*")
    return answer

def ProcessNameAnswer(answer):
    answer = answer.rstrip(".")
    return answer

def ProcessNumberAnswer(answer):
    answer = answer.replace(",", "")
    answer = answer.strip("*")
    return answer

def ProcessBoolAnswer(answer):
    answer = answer.rstrip(".")
    return answer

def RunNumberQuestions(llmClient, questionsAndAnswers, startTime=None, maxTimeInSeconds=0):
    total = 0
    succeeded = 0
    failed = 0
    stats = {}
    stats['qaDetails'] = {}
    for qa in questionsAndAnswers:
        # Do the timeout check first
        if (not startTime is None) and (maxTimeInSeconds > 0):
            timeDiff = (datetime.now() - startTime).total_seconds()
            if timeDiff > maxTimeInSeconds:
                raise Exception('Timeout')
        qaDetails = {}
        question = qa['question']
        answer = qa['answer']
        #print(question, '=>', answer)
        prompt = 'From now on only answer with numbers.'
        question2 = prompt + ' ' + question
        resp = llmClient.TalkToLlm(question2, 'low')
        print(FormatElapsed(startTime), question, answer, '=>', '"'+resp+'"')
        resp = ProcessNumberAnswer(resp)
        total += 1
        if answer.lower() == resp.lower():
            succeeded += 1
            qaDetails['succeeded'] = True
        else:
            failed += 1
            qaDetails['succeeded'] = False
            print('!!!!!!!!!!!!!')
        stats['qaDetails'][question] = qaDetails
    stats['total'] = total
    stats['succeeded'] = succeeded
    stats['failed'] = failed
    return stats

def RunNamesQuestions(llmClient, questionsAndAnswers, startTime=None, maxTimeInSeconds=0):
    total = 0
    succeeded = 0
    failed = 0
    stats = {}
    stats['qaDetails'] = {}
    for qa in questionsAndAnswers:
        # Do the timeout check first
        if (not startTime is None) and (maxTimeInSeconds > 0):
            timeDiff = (datetime.now() - startTime).total_seconds()
            if timeDiff > maxTimeInSeconds:
                raise Exception('Timeout')
        qaDetails = {}
        question = qa['question']
        answer = qa['answer']
        prompt = 'From now on only answer with names.'
        question2 = prompt + ' ' + question
        #print(question, '=>', answer)
        resp = llmClient.TalkToLlm(question2, 'low')
        print(FormatElapsed(startTime), question, answer, '=>', '"'+resp+'"')
        resp = ProcessNameAnswer(resp)
        total += 1
        if CheckResponse(answer, resp):
            succeeded += 1
            qaDetails['succeeded'] = True
        else:
            failed += 1
            qaDetails['succeeded'] = False
            print('!!!!!!!!!!!!!')
        stats['qaDetails'][question] = qaDetails
    stats['total'] = total
    stats['succeeded'] = succeeded
    stats['failed'] = failed
    return stats

def FormatElapsed(startTime):
    if startTime is None:
        return None
    timeDiff = (datetime.now() - startTime).total_seconds()
    timeDiff = int(timeDiff)
    td = timedelta(seconds=timeDiff)
    #return '[+{0}s]'.format(timeDiff)
    return '[+{0}]'.format(str(td))

def RunBooleanQuestions(llmClient, questionsAndAnswers, startTime=None, maxTimeInSeconds=0):
    total = 0
    succeeded = 0
    failed = 0
    stats = {}
    stats['qaDetails'] = {}
    for qa in questionsAndAnswers:
        # Do the timeout check first
        if (not startTime is None) and (maxTimeInSeconds > 0):
            timeDiff = (datetime.now() - startTime).total_seconds()
            if timeDiff > maxTimeInSeconds:
                raise Exception('Timeout')
        qaDetails = {}
        question = qa['question']
        answer = qa['answer']
        prompt = 'From now on only answer with "true" or "false".'
        question2 = prompt + ' ' + question
        #print(question, '=>', answer)
        resp = llmClient.TalkToLlm(question2, 'low')
        print(FormatElapsed(startTime), question, answer, '=>', '"'+resp+'"')
        resp = ProcessBoolAnswer(resp)
        total += 1
        if CheckResponse(answer, resp):
            succeeded += 1
            qaDetails['succeeded'] = True
        else:
            failed += 1
            qaDetails['succeeded'] = False
            print('!!!!!!!!!!!!!')
        stats['qaDetails'][question] = qaDetails
    stats['total'] = total
    stats['succeeded'] = succeeded
    stats['failed'] = failed
    return stats

def CheckResponse(expectedAnswers, llmAnswer):
    if type(expectedAnswers) == list:
        for ea in expectedAnswers:
            if ea.lower() == llmAnswer.lower():
                return True
        return False
    elif type(expectedAnswers) == str:
        return expectedAnswers.lower() == llmAnswer.lower()
    raise Exception('Unsupported type:', expectedAnswers)

def CombineStats(stats):
    total = 0
    succeeded = 0
    failed = 0
    res = {}
    res['qaDetails'] = {}
    for st in stats:
        total += st['total']
        succeeded += st['succeeded']
        failed += st['failed']
        res['qaDetails'].update(st['qaDetails'])
    res['total'] = total
    res['succeeded'] = succeeded
    res['failed'] = failed
    return res

def PrintModels(client):
    models = client.GetModelNames()
    print(models)

def BenchmarkModelAndGetStats(client, targetModel, maxTimeInSeconds=0):
    print('========================================================================')
    print('Loading model', targetModel, '...')
    client.StartConversation(targetModel)
    resp = client.TalkToLlm('Are you ready?')
    print('Ready? ->', resp)
    print('------------------------------------------------------------------------')

    startTime = datetime.now()
    print('Starting benchmarking for model', targetModel, 'at', startTime)

    # print('Initializing context...')
    # PrepareForBenchmarking(client)

    with open('qa-yesno.json', 'r') as file:
        qandas = json.load(file)
        PrepareForYesNoBenchmarking(client)
        res1 = RunYesNoQuestions(client, qandas, startTime, maxTimeInSeconds)
        print(res1)

    with open('qa-numbers.json', 'r') as file:
        qandas = json.load(file)
        # PrepareForYesNoBenchmarking(client)
        res2 = RunNumberQuestions(client, qandas, startTime, maxTimeInSeconds)
        print(res2)

    with open('qa-names.json', 'r') as file:
        qandas = json.load(file)
        # PrepareForYesNoBenchmarking(client)
        res3 = RunNamesQuestions(client, qandas, startTime, maxTimeInSeconds)
        print(res3)

    with open('qa-boolean.json', 'r') as file:
        qandas = json.load(file)
        res4 = RunBooleanQuestions(client, qandas, startTime, maxTimeInSeconds)
        print(res4)

    endTime = datetime.now()
    print('Benchmarking for model', targetModel, 'completed at', endTime)

    stats = CombineStats([res1, res2, res3, res4])
    stats['startTime'] = startTime
    stats['endTime'] = endTime
    timeElapsed = endTime - startTime
    print('Duration:', timeElapsed)
    stats['duration'] = timeElapsed
    return stats

def BenchmarkModel(client, targetModel, maxTimeInSeconds=0, appendToTsvStats=False):
    stats = BenchmarkModelAndGetStats(client, targetModel, maxTimeInSeconds)
    print('--------------------------------------')
    #print(stats)
    print('Model:', targetModel)
    successRate = stats['succeeded'] / stats['total']
    print('Success rate:', successRate)
    stats['successRate'] = successRate
    SaveRunStatsToFile(targetModel, stats, appendToTsvStats)

def SaveRunStatsToFile(targetModel, stats, appendToTsvStats):
    if not os.path.isdir('reports'):
        os.mkdir('reports')
    fileName = 'reports/' + targetModel.replace('/', '_') + '.json'
    with open(fileName, 'w') as file:
        file.write(str(stats))
    if appendToTsvStats:
        fileName = 'reports/model_stats.tsv'
        with open(fileName, 'a') as file:
            succeeded = stats['succeeded']
            failed = stats['failed']
            srate = succeeded / (succeeded + failed)
            duration = str(stats['duration'])
            file.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(targetModel, succeeded, failed, srate, duration))

def ReportTimeOut(model):
    if not os.path.isdir('reports'):
        os.mkdir('reports')
    fileName = 'reports/' + model.replace('/', '_') + '.timeout'
    with open(fileName, 'w') as file:
        file.write('Benchmarking timed out.')

def RunBenchmarksOnAllModels(client):
    filename = 'reports/model_stats.tsv'
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w') as file:
        file.write("Model name\tSucceeded\tFailed\tSuccessRate\tDuration\n")
    models = client.GetModelNames()
    cnt = 0
    for model in models:
        try:
            BenchmarkModel(client, model, 240, True)
            cnt += 1
            if cnt > 30:
                break
        except Exception as ex:
            msg = getattr(ex, 'message', repr(ex))
            print('Exception while testing model', model, ', msg:', msg)
            if 'timeout' in msg.lower():
                ReportTimeOut(model)

def BenchmarkQuestions(client):
    models = client.GetModelNames()
    questionCounts = {}
    cnt = 0
    for model in models:
        cnt += 1
        try:
            print(cnt, 'Benchmarking', model, '...')
            stats = BenchmarkModelAndGetStats(client, model, 240)
            # Increments the counts
            for question, details in stats['qaDetails'].items():
                if not question in questionCounts:
                    questionCounts[question] = {'success':0, 'failed':0}
                if details['succeeded']:
                    questionCounts[question]['success'] += 1
                else:
                    questionCounts[question]['failed'] += 1
            if cnt > 30:
                break
        except Exception as ex:
            print('Exception while testing model', model)
            msg = getattr(ex, 'message', repr(ex))
    for details in questionCounts.values():
        details['successRate'] = details['success'] / (details['success'] + details['failed'])
    print(questionCounts)
    if not os.path.isdir('reports'):
        os.mkdir('reports')
    fileName = 'reports/questions_stats.json'
    with open(fileName, 'w') as file:
        file.write(str(questionCounts))


if len(sys.argv) <= 1 or (len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '-help')):
    print('Usage (v.0.01):')
    print('-m MODEL_NAME    <-- run the benchmark against a single model')
    print('-f FILE_NAME     <-- run the benchmark against a list of models in a text file (one model name per line)')
    print('-runall          <-- runs the benchmark against all available models')
    print('-list_models     <-- returns the list of available models')
    print('-bmq             <-- benchmark the questions')
    print('-h or -help      <-- prints this')
    exit()

lmStudioUrl = 'http://localhost:1234/v1'

if len(sys.argv) == 2:
    oper = sys.argv[1]
    if oper == '-list_models':
        client = LocalLlmClient(lmStudioUrl)
        PrintModels(client)
        exit()
    elif oper == '-runall':
        client = LocalLlmClient(lmStudioUrl)
        RunBenchmarksOnAllModels(client)
        exit()
    elif oper == '-bmq':
        client = LocalLlmClient(lmStudioUrl)
        BenchmarkQuestions(client)
        exit()
if len(sys.argv) == 3:
    oper = sys.argv[1]
    if oper == '-m':
        modelName = sys.argv[2]
        client = LocalLlmClient(lmStudioUrl)
        models = client.GetModelNames()
        if not modelName in models:
            print('Model name is not on the list of available models.')
            exit()
        BenchmarkModel(client, modelName)
        exit()
print('Unsupported params!')
exit()
