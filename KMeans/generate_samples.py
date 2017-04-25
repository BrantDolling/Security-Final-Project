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



#TODO: Create function to check accuracy. Function will both have to determine the percentage of attack versus non attack in each cluster.
#  Attack versus non-attack ips are found in the file ips.text. IP address is the first field in the
#connection tensor.
#List of attack ips and user ips.
# Future useage, remember list of attack ips.
#Then look at returned samples and dermine the percentage of attack ips/user ips in each.
#To turn string ips to ints. Do turnIptoInt(string_ip).
#sample_values is a list that stores the connections as [ip,average_datetime_diff,...] etc. ip is always the first value.
#Group 1 can be accessed with connection_groups[0].
#Group 2 can be accessed with connection_groups[1].

#plot
plot_clusters(connection_groups, updated_centroid_value)
