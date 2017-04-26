import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import netaddr
import matplotlib.pyplot as plt
from FTPLogReader.FTPLogReader import FTPLogReader

#TODO: Modify so that code works with created samples



"""TODO:
    Returns the connection and centroid tensors.
   Will have to be fed in through a feed dict
   Args:
        nclusters (int): number of clusters.
        log_file (string): FTP Log file.
    Returns: connection_tensor """
def get_FTP_tensors(log_file):
    reader = FTPLogReader(log_file, 0)
    connections = reader.getConnectionTensors()

    return tf.constant(connections,dtype=tf.double)

#Returns true if the sum of the connections within a centroid drops below a certain value.
#TODO: Figure out how to determine a good threshold.
#A stopping condition is described here :https://nlp.stanford.edu/IR-book/html/htmledition/k-means-1.html
 #Bascially take the sum of distances in each cluster and attempt to get that value below a threshold.
def should_stop(connection_groups,centroids,threshold):

    #Calculate the sum
    sum = 0
    for i, centroid in enumerate(centroids):
        # Grab just the samples for the given cluster. np.delete removes the IP addresses.
        samples = np.delete(connection_groups[i],0,axis=1)
        distances = np.sum(np.square(samples-centroid),1)

        sum += np.sum(distances)

    if sum < threshold:
        return True
    else:
        return False

def create_samples(n_clusters, n_samples_per_cluster, n_features, embiggen_factor, seed):
    np.random.seed(seed)
    slices = []
    centroids = []
    # Create samples for each cluster
    for i in range(n_clusters):
        #Creates a bunch of random points with normal distribution.
        samples = tf.random_normal((n_samples_per_cluster, n_features),mean=0.0, stddev=5.0, dtype=tf.float32, seed=seed, name="cluster_{}".format(i))
        #Creates random centroid
        current_centroid = (np.random.random((1, n_features)) * embiggen_factor) - (embiggen_factor/2)
        centroids.append(current_centroid)
        #Make samples center around this centroid
        samples += current_centroid
        #centroid is the same as the sample
        slices.append(samples)
    # Create a big "samples" dataset
    samples = tf.concat(slices, 0, name='samples')
    centroids = tf.concat(centroids, 0, name='centroids')
    return centroids, samples

#TODO: Find a nice way to represent these.
#Right now plots Ip versus the sum of the statuses
def plot_clusters(connection_groups, centroids):
     #Plot out the different clusters
     #Choose a different colour for each cluster
     colour = plt.cm.rainbow(np.linspace(0,1,len(centroids)))
     for i, centroid in enumerate(centroids):
         #Grab just the samples for the given cluster and plot them out with a new colour
         samples = connection_groups[i]
         plt.scatter(samples[:,1], samples[:,2]+samples[:,3]+samples[:,4], c=colour[i])
         #Also plot centroid
         plt.plot(centroid[0], centroid[1], markersize=35, marker="x", color='k', mew=10)
         plt.plot(centroid[0], centroid[1], markersize=30, marker="x", color='m', mew=5)
     plt.show()

#This will be the same in our final version
def choose_random_centroids(samples, n_clusters):

    #Remove the IP addresses from the calculation
    samples = removeIps(samples)

    # Step 0: Initialisation: Select `n_clusters` number of random points
    #Have to subtract one here to ignore IP addresses.
    n_samples = tf.subtract(tf.shape(samples)[0],tf.constant(1,dtype=tf.int32))
    random_indices = tf.random_shuffle(tf.range(0, n_samples))
    begin = [0,]
    size = [n_clusters,]
    size[0] = n_clusters
    centroid_indices = tf.slice(random_indices, begin, size)
    initial_centroids = tf.gather(samples, centroid_indices)
    return initial_centroids


# Finds the nearest centroid for each sample
#Returns a list where each element k the index of the nearest centroid in centroid.
#For example, [ 0,5,1,1...] indicates taht the first sample is closest to the first centroid, the second sample is closest to the 6th etc.
def assign_to_nearest(samples, centroids):

    #Remove the IP addresses from the calculation
    samples = removeIps(samples)

    # START from http://esciencegroup.com/2016/01/05/an-encounter-with-googles-tensorflow/
    #Adding a dimension to the vectors so that they can be correctly reduced.
    expanded_vectors = tf.expand_dims(samples, 0)
    expanded_centroids = tf.expand_dims(centroids, 1)

    #Calculating the distances.
    distances = tf.reduce_sum( tf.square(tf.subtract(expanded_vectors, expanded_centroids)), 2)
    mins = tf.argmin(distances, 0)

    # END from http://esciencegroup.com/2016/01/05/an-encounter-with-googles-tensorflow/
    nearest_indices = mins
    return nearest_indices

def update_centroids(samples, nearest_indices, n_clusters):

    # Updates the centroid to be the mean of all samples associated with it.
    nearest_indices = tf.to_int32(nearest_indices)
    partitions = tf.dynamic_partition(samples, nearest_indices, n_clusters)
    new_centroids = tf.concat([tf.expand_dims(tf.reduce_mean( removeIps(partition), 0), 0) for partition in partitions], 0)
    return new_centroids,partitions

#Converts the given ip into an interger.
def turnIptoInt(string_ip):
    return int(netaddr.IPAddress(string_ip))

#Removes the ip address from the given tensor
def removeIps(tensor):
    return tf.slice(tensor,[0,1],[-1,4])