
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
import os
import cubeTrain as ct

# Possible Values: FNN, CNN, RNN, MLN
NETWORK_TYPE = 'MLN'
DEPTH = 6

# Create a nxn Cube
orderNum = 2
ncube = cube.Cube(order=orderNum)


# Define the training parameters
training_epochs = 20
training_batches = 100
batch_size = 5000

# Verification Paramters
display_step = 1
test_data_size = 1000

# Solving Paramters
total_solv_trials = 100
solvable_limit = 50
solvable_step = 999999

# Define Network Topolgy
n_input = len(ncube.constructVectorState(inBits=True))
n_hidden_1 = 1024
n_hidden_2 = 512
n_hidden_3 = 256
n_output = 12     # There are only 12 possible actions.

# Define the layers of the MLN
mln_layers = 16
mln_info =[n_input] + [128]*mln_layers + [n_output]


# Create the input and output variables
x = tf.placeholder("float", [None, n_input])
y = tf.placeholder("float", [None, n_output])
keepratio = tf.placeholder(tf.float32)
stddev = 0.05

#
#   MULTILAYER NEURAL NETWORK STUFF
#
weights = {}
biases = {}

def initWeight(shape, stddev):
    return tf.Variable(tf.random_normal(shape,stddev=stddev))

def initBias(shape):
    return tf.Variable(tf.random_normal(shape))

def initLayer(x, w, b):
    lxw = tf.matmul(x, w)
    lb  = tf.add(lxw, b)
    lr  = tf.nn.relu(lb)
    return lr

def finalLayer(x, w, b, keep_prob):
    ld = tf.nn.dropout(x, keep_prob)
    lxw =tf.matmul(ld, w)
    lb = tf.add(lxw, b)
    return lb

def generateMLN(X, keep_prob, mlnInfo):
    for i in range(1,len(mlnInfo)):
        weights[i] = initWeight([mlnInfo[i-1], mlnInfo[i]],0.05)
        biases[i]  = initBias([mlnInfo[i]])
    layers = [X]
    i = 1
    for _ in range(1, len(mlnInfo)-1):
        layers.append(initLayer(layers[i-1], weights[i], biases[i]))
        i+=1
    layers.append(finalLayer(layers[i-1],weights[i], biases[i], keep_prob))
    return layers[-1]


#
#   FEED FORWARD STUFF TYPICAL NEURAL NETWORK
#
# network Parameters For 
if NETWORK_TYPE is 'FNN':
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
    x_3 = tf.nn.relu(tf.add(tf.matmul(layer_2, _weights['h3']), _biases['b3']))
    layer_3 = tf.nn.dropout(x_3, _keep_prob)
    return (tf.matmul(layer_3, _weights['out']) + _biases['out'])


#
#   CONVOLUTIONAL NEURAL NETWORK STFF
#
dimOrder = int(len(ncube.constructVectorState(inBits=True))**0.5)
numConvLayers = 2
cnv = dimOrder // (numConvLayers*2)

if NETWORK_TYPE is 'CNN':
    weights  = {
        'wc1': tf.Variable(tf.truncated_normal([3, 3, 1, 64], stddev=stddev)),
        'wc2': tf.Variable(tf.truncated_normal([3, 3, 64, 128], stddev=stddev)),
        'wc3': tf.Variable(tf.truncated_normal([3, 3, 128, 256], stddev=stddev)),
        'wd1': tf.Variable(tf.truncated_normal([cnv*cnv*256, 1024], stddev=stddev)),
        'wd2': tf.Variable(tf.truncated_normal([1024, n_output], stddev=stddev))
    }
    biases   = {
        'bc1': tf.Variable(tf.random_normal([64], stddev=0.1)),
        'bc2': tf.Variable(tf.random_normal([128], stddev=0.1)),
        'bc3': tf.Variable(tf.random_normal([256], stddev=0.1)),
        'bd1': tf.Variable(tf.random_normal([1024], stddev=0.1)),
        'bd2': tf.Variable(tf.random_normal([n_output], stddev=0.1))
    }


def CONV(_input, _w, _b, _keepratio):
    # INPUT
    _input_r = tf.reshape(_input, shape=[-1, dimOrder, dimOrder, 1])
    # CONV LAYER 1
    _conv1 = tf.nn.conv2d(_input_r, _w['wc1'], strides=[1, 1, 1, 1], padding='SAME')
    _mean, _var = tf.nn.moments(_conv1, [0, 1, 2])
    _conv1 = tf.nn.batch_normalization(_conv1, _mean, _var, 0, 1, 0.0001)
    _conv1 = tf.nn.relu(tf.nn.bias_add(_conv1, _b['bc1']))
    _pool1 = tf.nn.max_pool(_conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    _pool_dr1 = tf.nn.dropout(_pool1, _keepratio)
    # CONV LAYER 2
    _conv2 = tf.nn.conv2d(_pool_dr1, _w['wc2'], strides=[1, 1, 1, 1], padding='SAME')
    _mean, _var = tf.nn.moments(_conv2, [0, 1, 2])
    _conv2 = tf.nn.batch_normalization(_conv2, _mean, _var, 0, 1, 0.0001)
    _conv2 = tf.nn.relu(tf.nn.bias_add(_conv2, _b['bc2']))
    _pool2 = tf.nn.max_pool(_conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    _pool_dr2 = tf.nn.dropout(_pool2, _keepratio)
    # CONV LAYER 3
    _conv3 = tf.nn.conv2d(_pool_dr2, _w['wc3'], strides=[1,1,1,1], padding='SAME')
    _mean, _var = tf.nn.moments(_conv3, [0,1,2])
    _conv3 = tf.nn.batch_normalization(_conv3, _mean, _var, 0, 1, 0.0001)
    _conv3 = tf.nn.relu(tf.nn.bias_add(_conv3, _b['bc3']))
    #_pool3 = tf.nn.max_pool(_conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    #_pool_dr3 = tf.nn.dropout(_pool3, _keepratio)
    # VECTORIZE
    _dense1 = tf.reshape(_conv3, [-1, _w['wd1'].get_shape().as_list()[0]])
    # FULLY CONNECTED LAYER 1
    _fc1 = tf.nn.relu(tf.add(tf.matmul(_dense1, _w['wd1']), _b['bd1']))
    print(_fc1.get_shape())
    _fc_dr1 = tf.nn.dropout(_fc1, _keepratio)
    # FULLY CONNECTED LAYER 2
    _out = tf.add(tf.matmul(_fc_dr1, _w['wd2']), _b['bd2'])
    # RETURN
    out = { 'input_r': _input_r, 'conv1': _conv1, 'pool1': _pool1, 'pool1_dr1': _pool_dr1,
        'conv2': _conv2, 'pool2': _pool2, 'pool_dr2': _pool_dr2, 'dense1': _dense1,
        'fc1': _fc1, 'fc_dr1': _fc_dr1, 'out': _out
    }
    return out['out']


# Lets party

# Model 
if NETWORK_TYPE is 'FNN':
    model = FFNN(x, weights, biases, keepratio)
elif NETWORK_TYPE is 'CNN':
    model = CONV(x, weights, biases, keepratio)
elif NETWORK_TYPE is 'MLN':
    model = generateMLN(x, keepratio, mln_info)

# Cost Type
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(model, y))
# Optimizer
optm = tf.train.AdamOptimizer(learning_rate=0.001).minimize(cost)
# Correcion
corr = tf.equal(tf.argmax(model, 1), tf.argmax(y, 1))
# Accuracy
accr = tf.reduce_mean(tf.cast(corr, "float"))
# Prediction
pred = tf.argmax(model, 1)


# Initialize everything up to this point
init = tf.initialize_all_variables()
#init = tf.global_variables_initializer()
print("CUBENET NEURAL NETWORK (",NETWORK_TYPE,") IS READY. ")


# Create the Saver Object and directory to save in
saver = tf.train.Saver()
ckpt_dir = "./ckpt_dir"
if not os.path.exists(ckpt_dir):
    os.makedirs(ckpt_dir)


# Launch the tensorflow session
sess = tf.Session()
sess.run(init)


def testCube(test_size, token, solv_limit, display_step):
    solv_count = 0
    scrambles = ct.generateScrambles(scramble_size=test_size,
        max_len=DEPTH, token=token, orderNum=2)
    # Go through each scramble
    for scrIndex in range(test_size):
        ncube = cube.Cube(order=orderNum)
        # Actually scramble the cube
        for action in scrambles[scrIndex]:
            ncube.minimalInterpreter(action)
        actionList=[]
        if (scrIndex+1) % display_step == 0:
            ncube.displayCube(isColor=True)
        # Solving phase
        for _ in range(solv_limit):
            if ncube.isSolved():
                solv_count+=1
                break
            vectorState = []
            vectorState.append(ncube.constructVectorState(inBits=True))
            cubeState = np.array(vectorState, dtype='float32')
            # Apply the model
            dictTemp = {x:cubeState, keepratio:1.0}
            result = sess.run(pred, feed_dict=dictTemp)
            # Apply the result to the cube and save it
            actionList.append(ct.vectorToAction[list(result)[0]])
            ncube.minimalInterpreter(actionList[-1])
        if (scrIndex+1) % display_step == 0:
            ncube.displayCube(isColor=True)
            print("SCRAMBLE: ", scrambles[scrIndex])
            print("ACTION: ", actionList)
    print("Test Results (%s): %03d/%03d -> %.3f" % 
         (token, solv_count, test_size, solv_count/(test_size*1.0)))



# Start the training
print("\nTRAINING HAS BEGUN...\n")
for epoch in range(training_epochs):
    avg_cost = 0.0

    # Each Epoch goes through a large set of batches
    # The exact values are defined above
    # Each Batch is a unique randomly generated sequence
    # from the rubiks cube
    for i in range(training_batches):
        #print(i)
        batch_x, batch_y = ct.ncubeCreateBatch(batch_size, DEPTH,orderNum)
        dictTemp = {x: batch_x, y: batch_y, keepratio: 0.6}
        sess.run(optm, feed_dict=dictTemp)
        dictTemp = {x: batch_x, y: batch_y, keepratio: 1.0}
        avg_cost+=sess.run(cost,feed_dict=dictTemp)
    avg_cost = avg_cost / training_batches
    
    # Display details of the epoch at certain intervals
    if (epoch + 1) % display_step == 0:
        
        # Epoch Stats
        print("\n----------------------------------------------------------------")
        print("Epoch: %03d/%03d cost: %.9f" % (epoch+1, training_epochs, avg_cost))
        
        # Test Data Stats
        test_x, test_y = ct.ncubeCreateBatch(test_data_size, DEPTH, orderNum)
        dictTemp = {x: test_x, y: test_y, keepratio: 1.0}
        test_acc = sess.run(accr, feed_dict=dictTemp)
        print("Test Accuracy: %.3f" % (test_acc))
        
        # Solving Stats
        testCube(total_solv_trials,'BALANCED', solvable_limit, solvable_step)
        testCube(total_solv_trials,'RANDOM', solvable_limit, solvable_step)
        testCube(total_solv_trials,'FIXED', solvable_limit, solvable_step)

        # Save the model on every display stepped epoch
        save_path = saver.save(sess, ckpt_dir+"/model.ckpt")
        print("Model saved in File : %s" % save_path)

testCube(1000,'BALANCED', solvable_limit, solvable_step)
testCube(1000,'RANDOM', solvable_limit, solvable_step)
testCube(1000,'FIXED', solvable_limit, solvable_step)


# Training has been completed
print("Optimization Done!")
