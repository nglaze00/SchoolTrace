import pandas as pd
import networkx as nx
import datetime as dt

class Database():
    def __init__(self):
        self.graph = graph_hardcoded()  # networkx graph object, with node features is_classroom (bool) and teacher_name (str)
        self.schedules = pd.read_csv('schedules.csv')

        self.class_paths = pd.read_csv('class_paths.csv')

        self.compute_student_paths()

        self.student_paths = pd.read_csv('student_paths.csv')


    def compute_class_paths(self):
        # run Dijkstra's on class_paths
        paths = nx.algorithms.shortest_paths.generic.shortest_path(self.graph) # dict[a][b] = path from a to b
        # print(paths)
        for node1 in paths.keys():
            print(node1)
            for node2 in paths[node1].keys():
                self.class_paths = self.class_paths.append(pd.Series([node1, node2, paths[node1][node2]], index=self.class_paths.columns), ignore_index=True)

    def compute_student_paths(self):
        self.student_paths = pd.DataFrame(columns=['stud_id', 'path1', 'path2', 'path3', 'path4'])
        for i, row in self.schedules.iterrows():

            student_sched = list(row[['class1', 'class2', 'class3', 'class4', 'class5']])

            # print(student_sched)

            class_edges = [(student_sched[i], student_sched[i + 1]) for i in range(len(student_sched) - 1)]


            new_row = [row['stud_id']] + [list(map(int, list(self.class_paths.loc[(self.class_paths['class1'] == a) & (self.class_paths['class2'] == b)]['path'])[0][1:-1].split(',')))
                     for a, b in class_edges]

            self.student_paths = self.student_paths.append(
                pd.Series(new_row, index=self.student_paths.columns), ignore_index=True)
        self.student_paths.to_csv('student_paths.csv')


    def compute_interactions(self, stud_id, days_transmissable=7):
        """
        Returns list of ‘interactions’: list of class #s at which overlaps occur, or tuples of class #s between which overlaps occur
        """
        paths = [list(map(int, self.student_paths[self.student_paths['stud_id'] == stud_id][
                                  ['path1', 'path2', 'path3', 'path4']].iloc[0][i][1:-1].split(','))) for i in range(4)]

        class_inter, walk_inter = [], []
        for i, row in self.student_paths.iterrows():
            if row['stud_id'] == stud_id or not self.schedules['is_positive'][self.schedules['stud_id'] == row['stud_id']].all():
                continue
            date_quarantined = dt.datetime(*map(int, self.schedules[self.schedules['stud_id'] == row['stud_id']]['date_started_quarantine'].tolist()[0].split('-')))

            if (dt.datetime.now() - date_quarantined).days > days_transmissable:
                continue
            # o_paths = [set(r) for r in ]
            o_paths = []
            for p in row[['path1', 'path2', 'path3', 'path4']]:
                o_paths.append(list(map(int, p[1:-1].split(','))))
            # print(row[['path1', 'path2', 'path3', 'path4']])
            # print(paths, o_paths)
            found_pds = set()
            for i, (path, o_path) in enumerate(zip(paths, o_paths)):

                if path[0] in o_path and i+1 not in found_pds:
                    class_inter.append((i + 1, path[0])) # which class period, which node
                    found_pds.add(i+1)
                if path[-1] in o_path and i+2 not in found_pds:
                    class_inter.append((i + 2, path[-1]))  # which class period, which node
                    found_pds.add(i + 2)
                for p in path[1:-1]:
                    if p in o_path and (i+1, i+2) not in found_pds:
                        walk_inter.append(((i+1, i+2), (path[0], path[-1]))) # (prev pd, next pd), (prev node, next node)
                        found_pds.add((i+1, i+2))

        return class_inter, walk_inter


    def formatted_interactions(self, stud_id, days_transmissable=7):
        class_inter, walk_inter = self.compute_interactions(stud_id, days_transmissable)


        res = 'Hi, ' + self.schedules.loc[self.schedules['stud_id'] == stud_id, 'stud_name'].iloc[0] + '\n'
        res += 'In the past week, you\'ve had up to {} daily interactions with COVID-positive students. \n'.format(len(class_inter) + len(walk_inter))
        if len(class_inter) > 0:
            res += 'Each day, you shared classrooms with up to {} COVID-positive students: \n'.format(len(class_inter))
            for period, classroom in sorted(class_inter, key=lambda x:x[0]):
                res += '    Period {} (Teacher: {}) \n'.format(period, self.graph.nodes[classroom]['teacher_name'])
        if len(walk_inter) > 0:
            res += 'Each day, you passed up to {} COVID-positive students in the halls: \n'.format(len(walk_inter))
            for (p1, p2), (c1, c2) in sorted(walk_inter, key=lambda x:x[0]):
                res += '    Between periods {} and {} (Teachers: {} and {}) \n'.format(p1, p2, self.graph.nodes[c1]['teacher_name'], self.graph.nodes[c2]['teacher_name'])
        return res

    def validate_login(self, user, password):
        students = self.schedules.loc[(self.schedules['user'] == user) & (self.schedules['pass'] == password)]

        if len(students) == 1:
            return students['stud_id'].tolist()[0]
        else:
            return None



def schedules_hardcoded():
    schedules = pd.DataFrame(
        columns=['stud_id', 'stud_name', 'user', 'pass', 'class1', 'class2', 'class3', 'class4', 'class5',
                 'is_positive', 'date_started_quarantine'])
    students = [['1345', 'Bill Jobs', 'BJobs', '1345', 1, 7, 21, 25, 3, False, None],
                ['6535', 'Thanos Simar', 'TSimar', '6535', 24, 4, 3, 1, 31, False, None],
                ['4584', 'Steve Gates', 'SGates', '4584', 31, 33, 25, 4, 1, False, None],
                ['5678', 'Jeff Musk', 'JMusk', '5678', 27, 24, 26, 3, 6, False, None],
                ['4325', 'Bill Bob', 'BBob', '4325', 31, 32, 33, 21, 22, False, None],
                ['5634', 'Elon Bezos', 'EBezos', '5634', 1, 7, 21, 25, 3, True, dt.datetime(2020,7,17)],
                ['1023', 'Dojo Woods', 'DWoods', '1023', 4, 31, 7, 26, 3, True, dt.datetime(2020,6,23)],
                ['9087', 'Gary Knightly', 'GKnightly', '9087', 21, 4, 1, 25, 5, True, dt.datetime(2020,7,13)],
                ['7494', 'Edward Orchard', 'EOrchard', '7494', 33, 21, 27, 4, 7, True, dt.datetime(2020,2,7)],
                ['3567', 'Peter Pan', 'PPan', '3567', 26, 25, 24, 23, 22, True, dt.datetime(2020,2,23)],
                ['1324', 'Juan Johnson', 'JJohnson', '1324', 31, 4, 26, 32, 22, True, dt.datetime(2020,5,16)]]

    for s in students:
        schedules = schedules.append(pd.Series(s, index=schedules.columns), ignore_index=True)
    schedules.to_csv('schedules.csv')


def graph_hardcoded():
    G = nx.Graph()
    d =  {
    1:(set([43]),True,"Finley"),
    2:(set([44]),True,"Boshernitzan"),
    3:(set([45]),True,"Dickinson"),
    4:(set([46]),True,"Lewis"),
    5:(set([47]),True,"Caprette"),
    6:(set([48]),True,"Belik"),
    7:(set([48]),True,"Brake"),
    8:(set([49,9]),True,"Suarez-Potts"),
    9:(set([8,49,54]),True,"Richards-Kortum"),
    10:(set([56,11]),True,"Gilbertson"),
    11:(set([10,12,57]),True,"Pellis"),
    12:(set([11,13]),True,"Senftle"),
    13:(set([12,58]),True,"Nakleh"),
    14:(set([62]),True,"Akin"),
    15:(set([63]),True,"Glick"),
    16:(set([64]),True,"Vardi"),
    17:(set([18,66]),True,"Huchette"),
    18:(set([17,19,20]),True,"Calabrese"),
    19:(set([18]),True,"Kamins"),
    20:(set([18]),True,"Rixner"),
    21:(set([77]),True,"Chehab"),
    22:(set([78]),True,"Martin"),
    23:(set([78]),True,"Huang"),
    24:(set([79]),True,"Novotny"),
    25:(set([44]),True,"Zubarev"),
    26:(set([45]),True,"Nelson"),
    27:(set([46]),True,"Fanger"),
    28:(set([47,48]),True,"Loos"),
    29:(set([49,50]),True,"Beaudrot"),
    30:(set([53]),True,"Guerra"),
    31:(set([72]),True,"Nunn"),
    32:(set([71]),True,"Drezek"),
    33:(set([73]),True,"Vassallo-Fernando"),
    34:(set([52,77,78]),True,"Carter"),
    35:(set([39,71]),True,"Winningham"),
    36:(set([59]),True,"Grenader"),
    37:(set([60]),True,"Bowdoin"),
    38:(set([63]),True,"Luan"),
    39:(set([35]),True,"Nichol"),
    40:(set([67]),True,"Flynn"),
    41:(set([68]),True,"Little"),
    42:(set([69]),True,"Takizawa"),


    43:(set([1,44,79]),False,""),
    44:(set([2,25,43,45]),False,""),
    45:(set([3,26,44,46]),False,""),
    46:(set([4,27,45,47]),False,""),
    47:(set([5,28,46,48]),False,""),
    48:(set([6,7,28,47,49]),False,""),
    49:(set([8,9,29,48,50]),False,""),
    50:(set([29,49,51]),False,""),
    51:(set([50,52,53]),False,""),
    52:(set([34,51]),False,""),
    53:(set([30,51,54,56]),False,""),
    54:(set([9,53,55]),False,""),
    55:(set([54]),False,""),
    56:(set([10,53,57]),False,""),
    57:(set([11,56,58,72]),False,""),
    58:(set([13,57,59]),False,""),
    59:(set([36,58,60,61]),False,""),
    60:(set([37,59,61,62]),False,""),
    61:(set([59,60]),False,""),
    62:(set([14,60,63]),False,""),
    63:(set([38,15,62,64]),False,""),
    64:(set([63,16,65]),False,""),
    65:(set([64,66]),False,""),
    66:(set([17,65,67]),False,""),
    67:(set([40,66,68]),False,""),
    68:(set([41,67,69]),False,""),
    69:(set([42,68,70]),False,""),
    70:(set([69,71,73]),False,""),
    71:(set([32,35,70,72]),False,""),
    72:(set([31,71,57]),False,""),
    73:(set([33,70,74]),False,""),
    74:(set([73,75]),False,""),
    75:(set([74,76]),False,""),
    76:(set([75,77]),False,""),
    77:(set([21,34,76,78]),False,""),
    78:(set([22,23,34,77,79]),False,""),
    79:(set([24,78,43]),False,"")
    }
    for id, (nbrs, is_classroom, teacher_name) in d.items():
        attrs = {'is_classroom': is_classroom}
        if is_classroom:
            attrs['teacher_name'] = teacher_name
        G.add_node(id, **attrs)
        G.add_edges_from([(id, nbr) for nbr in nbrs])
    return G

db = Database()
# test demos
# print(db.formatted_interactions(1345, 7))
# print(db.formatted_interactions(1345, 1))
# print(db.formatted_interactions(1345, 14))
# print(db.formatted_interactions(6535, 7))
# print(db.formatted_interactions(6535, 1))
# print(db.formatted_interactions(6535, 14))
# db.validate_login('BJobs', 1345)

