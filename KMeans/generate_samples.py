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

#TODO: Create samples from FTP log files.
#Store connection attempts as [ip,average_datetime_difference,ok_login_average,connect_average,fail_login_average]
#code started in functions.py get_FTP_tensors("LogFiles/mixed.log")
samples = get_FTP_tensors("LogFiles/mixed.log")

#Create variables/samples
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
        #TODO: FIgure out what partitions is returning. Figure out how to get sample clusters back.
        updated_centroid_value, new_samples = session.run(updated_centroids)
        print(sample_values)
        print(new_samples)
        #plot_clusters(sample_values, updated_centroid_value, n_samples_per_cluster)

        #Stopping condition.
        if should_stop(n_samples_per_cluster ,sample_values, updated_centroid_value, stop_threshold):
            break



#TODO: Create function to check accuracy. Function will both have to determine the percentage of attack versus non attack in each cluster.
#  Attack versus non-attack ips are found in the file ips.text. IP address is the first field in the
#connection tensor.
#List of attack ips and user ips.
# Future useage, remember list of attack ips.
#Then look at returned samples and dermine the percentage of attack ips/user ips in each.

#plot
plot_clusters(sample_values, updated_centroid_value, n_samples_per_cluster)
