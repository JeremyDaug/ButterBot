import pickle


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
            for i in curr.split(','):
                self.votes[valId][i.strip()] = []
            curr = val.split(reqs[3])[1].strip()  # votes
            self.votes[valId][reqs[3]] = int(curr)
        except IndexError as e:
            return None
        return valId

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
