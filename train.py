
# _             _                     
#| |_ _ __ __ _(_)_ __    _ __  _   _ 
#| __| '__/ _` | | '_ \  | '_ \| | | |
#| |_| | | (_| | | | | |_| |_) | |_| |
# \__|_|  \__,_|_|_| |_(_) .__/ \__, |
#                        |_|    |___/ 

# This is a Simple Feed-Forward Model.

import cube
import random
import tensorflow as tf
import numpy as np 

# Create a nxn Cube
orderNum = 2
ncube = cube.Cube(order=orderNum)

# Create the inverse Dictionary
actionInverse = {
    'r' : '.r',
    'l' :' .l',
    'u' : '.u',
    'd' : '.d',
    'f' : '.f',
    'b' : '.b',
    '.r': 'r',
    '.l':' l',
    '.u': 'u',
    '.d': 'd',
    '.f': 'f',
    '.b': 'b',
}

actionVector={
    'r' : [1,0,0,0,0,0,0,0,0,0,0,0],
    'l' : [0,1,0,0,0,0,0,0,0,0,0,0],
    'u' : [0,0,1,0,0,0,0,0,0,0,0,0],
    'd' : [0,0,0,1,0,0,0,0,0,0,0,0],
    'f' : [0,0,0,0,1,0,0,0,0,0,0,0],
    'b' : [0,0,0,0,0,1,0,0,0,0,0,0],
    '.r': [0,0,0,0,0,0,1,0,0,0,0,0],
    '.l': [0,0,0,0,0,0,0,1,0,0,0,0],
    '.u': [0,0,0,0,0,0,0,0,1,0,0,0],
    '.d': [0,0,0,0,0,0,0,0,0,1,0,0],
    '.f': [0,0,0,0,0,0,0,0,0,0,1,0],
    '.b': [0,0,0,0,0,0,0,0,0,0,0,1],
}

# Scrable Parameters
max_scramble = 6

def ncubeCreateBatch(batch_size):
    x_batch=[]
    y_batch=[]
    for _ in range(batch_size):
        ncube = cube.Cube(order=orderNum)
        scramble = []
        scramble_size = random.choice(max_scramble) + 1
        for _ in range(scramble_size):
            scramble.append(random.choice(actionVector.keys()))
        if len(scramble) > 1:
            scramble = cleanUpScramble(scramble)
        if scramble == []:
            scramble.append(random.choice(actionVector.keys()))
        for action in scramble:
            ncube.minimalInterpreter(action)
        x_batch.append(ncube.constructVectorState(inBits=True))
        y_batch.append(actionVector[scramble[-1]])

    return np.array(x_batch), np.array(y_batch)


def cleanUpScramble(scramble):
    i = 0
    while i < (len(scramble) - 1):
        if inverseAction[scramble[i]] == scramble[i+1]:
            del(scramble[i+1])
            del(scramble[i])
        else:
            i+=1
    return scramble


# Define Network Topolgy
n_input = len(ncube.constructVectorState(inBits=True))
n_hidden_1 = 64
n_hidden_2 = 64
n_hidden_3 = 32
n_output = 12     # There are only 12 possible actions.


# Create the input and output variables
x = tf.placeholder("float", [None, n_input])
y = tf.placeholder("float", [None, n_output])
dropout_keep_prob = tf.placeholder("float")


# network Parameters
stddev = 0.05
weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1], stddev=stddev)),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2], stddev=stddev)),
    'h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3], stddev=stddev)),
    'out': tf.Variable(tf.random_normal([n_hidden_3, n_output], stddev=stddev))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'b3': tf.Variable(tf.random_normal([n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_output]))
}


# Create the network
def FFNN(_X, _weights, _biases, _keep_prob):
    x_1 = tf.nn.relu(tf.add(tf.matmul(_X, _weights['h1']), _biases['b1']))
    layer_1 = x_1
    x_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, _weights['h2']), _biases['b2']))
    layer_2 = x_2
    x_2 = tf.nn.reul(tf.add(tf.matmul(layer_2, _weights['h3']), _biases['b3']))
    layer_3 = tf.nn.dropout(x_3, _keep_prob)
    return (tf.matmul(layer_3, _weights['out']) + _biases['out'])


# Lets party
model = FFNN(x, weights, biases, dropout_keep_prob)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(model, y))
optm = tf.train.AdamOptimizer(learning_rate=0.001).minimize(cost)
corr = tf.equal(tf.argmax(model, 1), tf.argmax(y, 1))
accr = tf.reduce_mean(tf.cast(corr, "float"))


init = tf.initialize_all_variables()
print("CUBENET FEED FORWARD NEURAL NETWORK IS READY.")


# Define the training parameters
training_epochs = 20
training_batches = 100
batch_size = 100
display_step = 4

# Launch the tensorflow session
sess = tf.Session()
sess.run(init)


# Start the training
for epoch in range(training_epochs):
    avg_cost = 0.0
