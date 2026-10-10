package main

import (
	"encoding/json"
	"os"
	"sync"
	"time"
)

func main() {
	values := make([]int, 6)
	limit := make(chan struct{}, 2)
	var wg sync.WaitGroup
	var mu sync.Mutex
	active, maxActive := 0, 0
	for i := range values {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()
			limit <- struct{}{}
			defer func() { <-limit }()
			mu.Lock()
			active++
			if active > maxActive {
				maxActive = active
			}
			mu.Unlock()
			time.Sleep(30 * time.Millisecond)
			values[index] = index * 2
			mu.Lock()
			active--
			mu.Unlock()
		}(i)
	}
	wg.Wait()
	if err := json.NewEncoder(os.Stdout).Encode(map[string]any{"values": values, "max_active": maxActive}); err != nil {
		panic(err)
	}
}
