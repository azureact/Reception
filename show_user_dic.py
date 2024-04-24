import pickle
try:
    with open("users_dic.pkl", "rb") as file:
        users_dic = pickle.load(file)
except:
    users_dic = {}

print(users_dic)