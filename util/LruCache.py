#-*- coding:utf-8 -*-

import collections
import threading
import datetime


class LruCache(object):
    USING_DELETE_STYLE = False

    def __init__(self, maxSize):
        super(LruCache, self).__init__()

        if maxSize < 0:
            raise ValueError("maxSize <= 0")

        self.mMaxSize = maxSize
        self.lockObject = threading.Lock()
        self.mCache = collections.OrderedDict()

        # Size of this cache in units. Not necessarily the number of elements.
        self.mSize = 0

        self.mPutCount = 0
        self.mCreateCount = 0
        self.mEvictionCount = 0
        self.mHitCount = 0
        self.mMissCount = 0

    def lock(self):
        self.lockObject.acquire()

    def unlock(self):
        self.lockObject.release()

    def __contains__(self, key):
        if not key:
            raise ValueError("key == None")

        """
        Returns True or False depending on whether or not the key is in the
        cache
        """
        return key in self.mCache

    #
    # Sets the size of the cache.
    #
    # @param maxSize The new maximum size.
    #
    def resize(self, maxSize):
        if maxSize < 0:
            raise ValueError("maxSize <= 0")

        self.lock()
        self.mMaxSize = maxSize
        self.unlock()

        self.trimToSize(self.mMaxSize)

    def putWithAccessTime(self, key, value):
        self.mCache[key] = {
            'last_accessed': datetime.datetime.now(),
            'value': value}

    def getWithAccessTime(self, key):
        mapDict = self.mCache[key]
        assert(mapDict)
        mapDict['last_accessed'] = datetime.datetime.now()
        return mapDict['value']

    def popWithAccessTime(self, key):
        previous = None
        previousDict = self.mCache.pop(key, None)
        if previousDict:
            previous = previousDict['value']
        return previous

    def eldest(self):
        oldestKey = None
        for key in self.mCache:
            if oldestKey is None:
                oldestKey = key
            elif self.mCache[key]['last_accessed'] < self.mCache[oldestKey]['last_accessed']:
                oldestKey = key
        return oldestKey

    #
    # Returns the value for {@code key} if it exists in the cache or can be
    # created by {@code #create}. If a value was returned, it is moved to the
    # head of the queue. This returns None if a value is not cached and cannot
    # be created.
    #

    def get(self, key):
        # self.log(">> get: key:{}".format(key))
        if not key:
            raise ValueError("key == None")

        mapValue = None
        self.lock()
        if LruCache.USING_DELETE_STYLE:
            mapValue = self.popWithAccessTime(key)
            if mapValue:
                self.putWithAccessTime(key, mapValue)
                self.mHitCount += 1
                self.unlock()
                return mapValue
        else:
            if key in self.mCache:
                mapValue = self.getWithAccessTime(key)
                if mapValue:
                    self.mHitCount += 1
                    self.unlock()
                    return mapValue

        self.mMissCount += 1
        self.unlock()

        #
        # Attempt to create a value. This may take a long time, and the map
        # may be different when create() returns. If a conflicting value was
        # added to the map while create() was working, we leave that value in
        # the map and release the created value.
        #

        createdValue = self.create(key)
        if not createdValue:
            return None

        self.lock()
        self.mCreateCount += 1
        self.putWithAccessTime(key, createdValue)

        self.mSize += self.safeSizeOf(key, createdValue)
        self.unlock()

        if mapValue:
            self.entryRemoved(False, key, createdValue, mapValue)
            return mapValue
        else:
            self.trimToSize(self.mMaxSize)
            return createdValue

    #
    # Caches {@code value} for {@code key}. The value is moved to the head of
    # the queue.
    #
    # @return the previous value mapped by {@code key}.
    #
    def put(self, key, value):
        # self.log(">> put: key:{}, value:{}".format(key, value))
        if not key or not value:
            raise ValueError("key == None || value == None")

        previous = None
        self.lock()
        self.mPutCount += 1
        self.mSize += self.safeSizeOf(key, value)
        previous = self.popWithAccessTime(key)
        self.putWithAccessTime(key, value)
        if previous:
            self.mSize -= self.safeSizeOf(key, previous)
        self.unlock()
        if previous:
            self.entryRemoved(False, key, previous, value)
        self.trimToSize(self.mMaxSize)
        return previous

    #
    # Remove the eldest entries until the total of remaining entries is at or
    # below the requested size.
    #
    # @param maxSize the maximum size of the cache before returning. May be -1
    #            to evict even 0-sized elements.
    #
    def trimToSize(self, maxSize):
        while True:
            key = None
            value = None

            self.lock()
            if self.mSize < 0 or (len(self.mCache) == 0 and self.mSize != 0):
                raise ValueError("sizeOf() is reporting inconsistent results!")

            if self.mSize <= maxSize:
                self.unlock()
                break

            if LruCache.USING_DELETE_STYLE:
                (key, value) = self.mCache.popitem(False)
            else:
                key = self.eldest()
                value = self.popWithAccessTime(key)

            self.mSize -= self.safeSizeOf(key, value)
            self.mEvictionCount += 1
            self.unlock()

            self.entryRemoved(True, key, value, None)

    #
    # Removes the entry for {@code key} if it exists.
    #
    # @return the previous value mapped by {@code key}.
    #
    def remove(self, key):
        if not key:
            raise ValueError("key == None")

        previous = None
        self.lock()
        previous = self.popWithAccessTime(key)
        if previous:
            self.mSize -= self.safeSizeOf(key, previous)
        self.unlock()

        if previous:
            self.entryRemoved(False, key, previous, None)

        return previous

    #
    # Called for entries that have been evicted or removed. This method is
    # invoked when a value is evicted to make space, removed by a call to
    # {@link #remove}, or replaced by a call to {@link #put}. The default
    # implementation does nothing.
    #
    # <p>The method is called without synchronization: other threads may
    # access the cache while this method is executing.
    #
    # @param evicted True if the entry is being removed to make space, False
    #     if the removal was caused by a {@link #put} or {@link #remove}.
    # @param newValue the new value for {@code key}, if it exists. If non-None,
    #     this removal was caused by a {@link #put}. Otherwise it was caused by
    #     an eviction or a {@link #remove}.
    #
    def entryRemoved(self, evicted, key, oldValue, newValue):
        pass

    #
    # Called after a cache miss to compute a value for the corresponding key.
    # Returns the computed value or None if no value can be computed. The
    # default implementation returns None.
    #
    # <p>The method is called without synchronization: other threads may
    # access the cache while this method is executing.
    #
    # <p>If a value for {@code key} exists in the cache when this method
    # returns, the created value will be released with {@link #entryRemoved}
    # and discarded. This can occur when multiple threads request the same key
    # at the same time (causing multiple values to be created), or when one
    # thread calls {@link #put} while another is creating a value for the same
    # key.
    #
    def create(self, key):
        return None

    def safeSizeOf(self, key, value):
        result = self.sizeOf(key, value)
        if result < 0:
            raise ValueError("Negative size: {}={}".format(key, value))
        return result

    #
    # Returns the size of the entry for {@code key} and {@code value} in
    # user-defined units.  The default implementation returns 1 so that size
    # is the number of entries and max size is the maximum number of entries.
    #
    # <p>An entry's size must not change while it is in the cache.
    #
    def sizeOf(self, key, value):
        return 1

    #
    # Clear the cache, calling {@link #entryRemoved} on each removed entry.
    #
    def evictAll(self):
        self.trimToSize(-1)  # -1 will evict 0-sized elements

    #
    # For caches that do not override {@link #sizeOf}, this returns the number
    # of entries in the cache. For all other caches, this returns the sum of
    # the sizes of the entries in this cache.
    #
    def size(self):
        result = 0
        self.lock()
        result = self.mSize
        self.unlock()
        return result

    #
    # For caches that do not override {@link #sizeOf}, this returns the maximum
    # number of entries in the cache. For all other caches, this returns the
    # maximum sum of the sizes of the entries in this cache.
    #
    def maxSize(self):
        result = 0
        self.lock()
        result = self.mMaxSize
        self.unlock()
        return result

    #
    # Returns the number of times {@link #get} returned a value that was
    # already present in the cache.
    #
    def hitCount(self):
        result = 0
        self.lock()
        result = self.mHitCount
        self.unlock()
        return result

    #
    # Returns the number of times {@link #get} returned None or required a new
    # value to be created.
    #
    def missCount(self):
        result = 0
        self.lock()
        result = self.mMissCount
        self.unlock()
        return result

    #
    # Returns the number of times {@link #create(Object)} returned a value.
    #
    def createCount(self):
        result = 0
        self.lock()
        result = self.mCreateCount
        self.unlock()
        return result

    #
    # Returns the number of times {@link #put} was called.
    #
    def putCount(self):
        result = 0
        self.lock()
        result = self.mPutCount
        self.unlock()
        return result

    #
    # Returns the number of values that have been evicted.
    #
    def evictionCount(self):
        result = 0
        self.lock()
        result = self.mEvictionCount
        self.unlock()
        return result

    #
    # Returns a copy of the current contents of the cache, ordered from least
    # recently accessed to most recently accessed.
    #
    def snapshot(self):
        result = None
        self.lock()
        if LruCache.USING_DELETE_STYLE:
            result = collections.OrderedDict(self.mCache)
        else:
            result = collections.OrderedDict(
                sorted(self.mCache.items(),
                       key=lambda t: t[1]['last_accessed'],
                       reverse=False))
        self.unlock()
        return result

    def __str__(self):
        self.lock()
        accesses = self.mHitCount + self.mMissCount
        hitPercent = 0
        if accesses != 0:
            hitPercent = (100.0 * self.mHitCount / accesses)
        info = "LruCache[mSize={}, maxSize={}, hits={}, misses={}, hitRate={}%]".format(
            self.mSize, self.mMaxSize, self.mHitCount, self.mMissCount, hitPercent)
        self.unlock()
        return info

    def dump(self):
        current = self.snapshot()
        # current = self.mCache
        self.log("============= size:{} ==============".format(len(current)))
        self.log("cache: {}".format(self))
        for key, value in current.items():
            self.log("key={}, value={}, last accessed:{}".format(
                key, value['value'], value['last_accessed']))

    def log(self, info):
        print(info)

if __name__ == '__main__':
    cache = LruCache(7)
    cache.put(1, "1")
    cache.put(2, "2")
    cache.put(3, "3")
    cache.put(4, "4")
    cache.put(5, "5")
    cache.put(6, "6")
    cache.dump()

    cache.get(3)
    cache.dump()

    cache.put(1, "one")
    cache.dump()

    cache.put(7, "7")
    cache.dump()
    cache.put(8, "8")
    cache.dump()
    cache.put(9, "9")
    cache.dump()
