import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from FTPLogReader.FTPLogReader import FTPLogReader

#TODO: Modify so that code works with created amples



"""TODO:
    Returns the connection and centroid tensors.
   Will have to be fed in through a feed dict
   Args:
        nclusters (int): number of clusters.
        seed (int): seed used to create random clusters.
        log_file (string): FTP Log file.
    Returns: connection_tensor, centroid_tensor"""
def get_FTP_tensors(n_clusters,seed,log_file):
    np.random.seed(seed)
    connections = []
    centroids = []
    reader = FTPLogReader(log_file, 0)
    for line in reader.getConnectionTensors():
        connections.append(line)

    #TODO Assign each connection to random centroid
    #Create placeholder/feed_dict to hold connections and correctly return this so that it can used.

    return connections

#Returns true if the sum of the connections within a centroid drops below a certain value.
#TODO: Figure out how to determine a good threshold.
#A stopping condition is described here :https://nlp.stanford.edu/IR-book/html/htmledition/k-means-1.html
 #Bascially take the sum of distances in each cluster and attempt to get that value below a threshold.
def should_stop(n_samples_per_cluster,connections,centroids,threshold):


    #Calculate the sum
    sum = 0
    for i, centroid in enumerate(centroids):
        # Grab just the samples for the given cluster
        samples = connections[i * n_samples_per_cluster:(i + 1) * n_samples_per_cluster]
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
        samples = tf.random_normal((n_samples_per_cluster, n_features),
                                   mean=0.0, stddev=5.0, dtype=tf.float32, seed=seed, name="cluster_{}".format(i))
        #Creates random centroid
        current_centroid = (np.random.random((1, n_features)) * embiggen_factor) - (embiggen_factor/2)
        centroids.append(current_centroid)
        #Add centroid to the end of the samples list
        samples += current_centroid
        #centroid is the same as the sample
        slices.append(samples)
    # Create a big "samples" dataset
    samples = tf.concat(slices, 0, name='samples')
    centroids = tf.concat(centroids, 0, name='centroids')
    return centroids, samples

def plot_clusters(all_samples, centroids, n_samples_per_cluster):
     #Plot out the different clusters
     #Choose a different colour for each cluster
     colour = plt.cm.rainbow(np.linspace(0,1,len(centroids)))
     for i, centroid in enumerate(centroids):
         #Grab just the samples for the given cluster and plot them out with a new colour
         samples = all_samples[i*n_samples_per_cluster:(i+1)*n_samples_per_cluster]
         plt.scatter(samples[:,0], samples[:,1], c=colour[i])
         #Also plot centroid
         plt.plot(centroid[0], centroid[1], markersize=35, marker="x", color='k', mew=10)
         plt.plot(centroid[0], centroid[1], markersize=30, marker="x", color='m', mew=5)
     plt.show()

def choose_random_centroids(samples, n_clusters):
    # Step 0: Initialisation: Select `n_clusters` number of random points
    n_samples = tf.shape(samples)[0]
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


    # START from http://esciencegroup.com/2016/01/05/an-encounter-with-googles-tensorflow/
    #Changing the size of the vectors so that the subtraction works out.
    expanded_vectors = tf.expand_dims(samples, 0)
    expanded_centroids = tf.expand_dims(centroids, 1)

    #Calculating the distances.
    distances = tf.reduce_sum( tf.square(
               tf.subtract(expanded_vectors, expanded_centroids)), 2)
    mins = tf.argmin(distances, 0)

    # END from http://esciencegroup.com/2016/01/05/an-encounter-with-googles-tensorflow/
    nearest_indices = mins
    return nearest_indices

def update_centroids(samples, nearest_indices, n_clusters):
    # Updates the centroid to be the mean of all samples associated with it.
    nearest_indices = tf.to_int32(nearest_indices)
    partitions = tf.dynamic_partition(samples, nearest_indices, n_clusters)
    new_centroids = tf.concat([tf.expand_dims(tf.reduce_mean(partition, 0), 0) for partition in partitions], 0)
    return new_centroids,partitions
