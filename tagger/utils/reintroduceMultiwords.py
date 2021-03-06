import sys,re
def reintroduce(gold, pred, out):
    predFixes = pred.split(".")
    predAugmented = pred + ".reintro"#predFixes[0] + "-multi.conllu"# + predFixes[1]
    goldTrees = {}
    goldTree = []
    goldInd = 0
    predTrees = []
    containsMultiword = False
    with open(gold, "r") as goldFile:
        for line in goldFile:
            if line.startswith("#"): continue
            if line == "\n":
                goldInd += 1
            entries = line.split("\t")
            if "-" in entries[0] or "." in entries[0]:
                wordId = int(re.findall(r"[\w']+", entries[0])[0])
                if "." in entries[0]:
                    wordId +=1
                try:
                    goldTrees[goldInd][wordId] = line
                except:
                    goldTrees[goldInd] = {}
                    goldTrees[goldInd][wordId] = line

    predInd = 0
    wordInd = 1
    with open(pred, "r") as predFile:
        with open(out, "w") as output:
            for line in predFile:
                if line == "\n":
                    output.write(line)
                    predInd += 1
                    wordInd = 1
                else:
                    try:
                        output.write(goldTrees[predInd][wordInd])
                    except:
                        pass
                    output.write(line)
                    wordInd += 1
            
