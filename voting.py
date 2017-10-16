import pickle

opt = 'options'

class voting:
    def __init__(self):
        self.votes = dict()

    def create_vote(self, val):
        print(val)
        reqs = ['ID:', 'Q:', 'O:', 'N:']
        try:
            curr = val.split(reqs[0])[1].split(reqs[1])[0].strip()  # id
            valId = curr
            self.votes[curr] = dict()
            curr = val.split(reqs[1])[1].split(reqs[2])[0].strip()  # question
            self.votes[valId][reqs[1]] = curr
            curr = val.split(reqs[2])[1].split(reqs[3])[0].strip()  # options
            self.votes[valId][opt] = []
            for i in curr.split(','):
                self.votes[valId][opt].append(i.strip())
                self.votes[valId][i.strip()] = set()
            curr = val.split(reqs[3])[1].strip()  # votes
            self.votes[valId][reqs[3]] = int(curr)
        except IndexError as e:
            return None
        return valId

    def IDs(self):
        ret = ''
        for key in self.votes.keys():
            ret += key + ', '
        ret = ret[:-2]
        if not ret:
            ret = 'No open Votes Found'
        return ret

    def show_vote(self, ID):
        ret = '' + self.votes[ID]['Q:'] + '\n'
        for i in self.votes[ID][opt]:
            print(i)
            ret += i + ': ' + str(len(self.votes[ID][i])) + '\n'
        ret = ret[:-1]
        return ret

    def add_votes(self, val, voter):
        ID, ballots = val.split(':')
        if ID not in self.votes.keys():
            return "Invalid ID"
        ballots = [i.strip() for i in ballots.split(',')]
        print(ballots)
        if len(ballots) > self.votes[ID]['N:']:
            return "Too Many Votes"
        ballots = set(ballots)
        for i in ballots:
            if i not in self.votes[ID].keys():
                return "Invalid option %s" % i
        for i in ballots:
            self.votes[ID][i].add(voter)
        return "Voting taken for " + str(ballots)

    def open_votes(self):
        return self.votes.keys()

    def save_votes(self):
        pickle.dump(self.votes, open('save.p', 'wb'))

    def load_votes(self):
        self.votes = pickle.load(open('save.p', 'rb'))


if __name__ == '__main__':
    test = voting()
    test.load_votes()
    test.create_vote("Create Vote ID:0 Q:Pick a number!  O: 1, 2, 3 N: 3")
    print(test.votes)
    test.save_votes()
    test.create_vote("Create Vote Q:Pick a Number!")
