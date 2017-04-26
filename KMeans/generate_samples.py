import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np

from functions import *

#K means might not work
# Might not work with categorical information: https://arxiv.org/ftp/cs/papers/0603/0603120.pdf
# Note for report: data is influenced by initial data and does only go for local minimums

n_features = 2
n_clusters = 2
n_samples_per_cluster = 2
seed = 700
embiggen_factor = 70
max_iterations = 1
stop_threshold = 1

#Create variables/samples

samples = get_FTP_tensors("LogFiles/mixed.log")

#real_centroids,samples = create_samples(n_clusters, n_samples_per_cluster, n_features, embiggen_factor, seed)
initial_centroids = choose_random_centroids(samples, n_clusters)
nearest_indices = assign_to_nearest(samples, initial_centroids)
updated_centroids = update_centroids(samples, nearest_indices, n_clusters)

#Initialize variables in tensorflow
model = tf.global_variables_initializer()

#Run tensorflow
with tf.Session() as session:
    #Run the initial set up
    sample_values = session.run(samples)
    # Run the update.
    for _ in range(max_iterations):

        #TODO: feed new centroids back into the algorithm.
        #TODO: Figure out what partitions is returning. Figure out how to get sample clusters back.
        updated_centroid_value,connection_groups = session.run(updated_centroids)

        #print(sample_values)
        #print(new_samples)
        #plot_clusters(sample_values, updated_centroid_value, n_samples_per_cluster)

        #Stopping condition.
        if should_stop(connection_groups, updated_centroid_value,stop_threshold):
            break

#Determining the accuracy. Note, that due to a rounding error, the ip address values are changed when paritioned
#and so all ips are sorted into the Bad Ips.

ipFileReader = open("ips.txt", "r")
ipString = ipFileReader.readline()
goodIPs=[]

while True:
    ipString = ipFileReader.readline().replace("\n","")
    if(ipString == "attack ips"):
        break
    goodIPs.append(turnIptoInt(ipString))


goodCount=0
badCount=0

for ip in connection_groups[0]:
    if ( ip[0] in goodIPs ):
        goodCount+=1
    else:
        badCount+=1

print("Group 1 has %s good Ips out of 100 and %s Bad Ips out of 20."%(goodCount,badCount))

goodCount=0
badCount=0

for ip in connection_groups[1]:
    if ( ip[0] in goodIPs ):
        goodCount+=1
    else:
        badCount+=1

print("Group 2 has %s good Ips out of 100 and %s Bad Ips out of 20." % (goodCount, badCount))

#plot
plot_clusters(connection_groups, updated_centroid_value)
