package main

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"regexp"
	"strconv"
	"syscall"
	"time"
)

var integerPattern = regexp.MustCompile(`^-?(0|[1-9][0-9]*)$`)

func integer(value string, min, max int) (int, error) {
	if len(value) > 8 || !integerPattern.MatchString(value) {
		return 0, errors.New("invalid_query")
	}
	n, err := strconv.Atoi(value)
	if err != nil || n < min || n > max {
		return 0, errors.New("invalid_query")
	}
	return n, nil
}
func reply(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		log.Print(err)
	}
}
func handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		w.Header().Set("Allow", "GET")
		reply(w, 405, map[string]string{"error": "method_not_allowed"})
		return
	}
	var query url.Values
	if r.URL.Path == "/sum" || r.URL.Path == "/wait" {
		var err error
		query, err = url.ParseQuery(r.URL.RawQuery)
		if err != nil {
			reply(w, 400, map[string]string{"error": "invalid_query"})
			return
		}
	}
	switch r.URL.Path {
	case "/health":
		reply(w, 200, map[string]bool{"ok": true})
	case "/sum":
		a, e1 := integer(query.Get("a"), -1000000, 1000000)
		b, e2 := integer(query.Get("b"), -1000000, 1000000)
		if e1 != nil || e2 != nil {
			reply(w, 400, map[string]string{"error": "invalid_query"})
			return
		}
		reply(w, 200, map[string]int{"sum": a + b})
	case "/wait":
		raw := "50"
		if values, ok := query["ms"]; ok {
			raw = values[0]
		}
		ms, err := integer(raw, 0, 1000)
		if err != nil {
			reply(w, 400, map[string]string{"error": "invalid_query"})
			return
		}
		timer := time.NewTimer(time.Duration(ms) * time.Millisecond)
		defer timer.Stop()
		select {
		case <-timer.C:
			reply(w, 200, map[string]int{"waited_ms": ms})
		case <-r.Context().Done():
			return
		}
	default:
		reply(w, 404, map[string]string{"error": "not_found"})
	}
}
func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "3001"
	}
	server := &http.Server{Addr: "127.0.0.1:" + port, Handler: http.HandlerFunc(handler), ReadHeaderTimeout: 5 * time.Second, WriteTimeout: 5 * time.Second, IdleTimeout: 30 * time.Second}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	shutdownDone := make(chan struct{})
	go func() {
		defer close(shutdownDone)
		<-ctx.Done()
		shutdown, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := server.Shutdown(shutdown); err != nil {
			log.Print(err)
		}
	}()
	log.Printf("Go listening on %s", port)
	if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatal(err)
	}
	<-shutdownDone
}
