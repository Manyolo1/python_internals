import sys 
import gc 
import tracemalloc

from typing import Dict, List, Any
from dataclasses import dataclass
import weakref

# track memory leaks 

@dataclass(frozen=True)
class MemorySnapshot:
    timestamp: float
    heapSize: int 
    objectCount :int
    refcount: int 
    gc_collections: int
    


class MemoryProfiler:
    def __init__(self,track_objects:bool=True):
        
        self.snapshots: List[MemorySnapshot] = []
        self.trackedObjects: Dict[int,weakref.ref]={}
        self.track_objects = track_objects

        tracemalloc.start()

    def takeSnapshot(self) -> MemorySnapshot:
        curr, peak = tracemalloc.get_traced_memory()
        gc_stats = gc.get_stats()
        snapshot = MemorySnapshot(
            timestamp=gc.get_count()[0],
            heapSize=curr,
            objectCount=len(gc.get_objects()),
            refcount=sys.getrefcount(gc.get_objects()),
            gc_collections=sum(s['collections'] for s in gc_stats)
        )
        self.snapshots.append(snapshot)
        return snapshot
    
    
    def findCircularRef(self)->List[List[Any]]:
        gc.collect()
        circular_refs=[]
        for ob in gc.garbage:
            referrers = gc.get_referrers(ob)

            if any(ref is ob for ref in referrers):
                circular_refs.append(referrers)
        return circular_refs

    def estimatedSavedMemory(self, classWithSlots,classWithoutSlots, instances:int=1000):
        # instance w/o slots
        objDict = [classWithoutSlots() for _ in range(instances)]
        dict_size=sum(sys.getsizeof(obj.__dict__) for obj in objDict)

        # instances w slots
        objSlots=[classWithSlots() for _ in range(instances)]
        slots_size=sum(sys.getsizeof(obj) for obj in objSlots)

        mem_saved = dict_size - slots_size
        percent_saved = (mem_saved/dict_size)*100 if dict_size > 0 else 0
        return {
            "dict_based": dict_size,
            "slot_based":slots_size,
            "saved_bytes":mem_saved,
            "percent_saved":percent_saved,
        }
    
class OptimisedDataClass:
    # use of __slots__ for mem. optimisation
    __slots__ = ['x','y','z','_cached_sum']
    def __init__(self, x:float,y:float,z:float):
        self.x=x
        self.y=y
        self.z=z
        self._cached_sum=None

    @property
    def sum(self)->float:
        if self._cached_sum is None:
            self._cached_sum=self.x+self.y+self.z
        return self._cached_sum
    
    def __sizeof__(self):
        return object.__sizeof__(self)
    

if __name__=="__main__":
    profiler=MemoryProfiler()
    baseline=profiler.takeSnapshot()
    # baseline snapshot 
    print(f"Baseline - Heap: {baseline.heapSize} bytes, Objects: {baseline.objectCount}")

    testObj = [OptimisedDataClass(i,i+1,i+2) for i in range(10000)]

    after_alloc = profiler.takeSnapshot()
    delta=after_alloc.heapSize - baseline.heapSize

    print(f"After allocation - Delta: {delta} bytes")

    # triggering garbage collection by clean up
    del testObj
    gc.collect()

    # final snap
    final =profiler.takeSnapshot()
    print(f"After cleanup - Heap: {final.heapSize} bytes")



        





