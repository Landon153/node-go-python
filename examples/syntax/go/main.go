package main

import (
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"regexp"
	"slices"
	"strconv"
	"time"
	"unicode/utf8"
)

type User struct{ Name string }

func (u User) Greet() string { return "Hi, " + u.Name }
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}
func run() error {
	xs := []int{1, 2, 3, 4}
	copied := slices.Clone(xs)
	copied[0] = 99
	even, squared := []int{}, []int{}
	total := 0
	for _, x := range xs {
		if x%2 == 0 {
			even = append(even, x)
		}
		squared = append(squared, x*x)
		total += x
	}
	sorted := []int{10, 2, 1}
	slices.Sort(sorted)
	scores := map[string]int{"Ada": 9}
	_, hasMissing := scores["Bob"]
	_, divisionErr := divide(1, 0)
	var parsed struct {
		Active bool `json:"active"`
	}
	if err := json.Unmarshal([]byte(`{"active":true}`), &parsed); err != nil {
		return err
	}
	number, err := strconv.Atoi("42")
	if err != nil {
		return err
	}
	dir, err := os.MkdirTemp("", "node-go-python-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(dir)
	path := filepath.Join(dir, "hello.txt")
	if err := os.WriteFile(path, []byte("hello"), 0600); err != nil {
		return err
	}
	file, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	unique := []int{}
	seen := map[int]bool{}
	for _, x := range []int{1, 1, 2} {
		if !seen[x] {
			seen[x] = true
			unique = append(unique, x)
		}
	}
	bigNumber := new(big.Int).Lsh(big.NewInt(1), 60)
	bigNumber.Add(bigNumber, big.NewInt(1))
	output := map[string]any{
		"greeting": (User{Name: "Ada"}).Greet(), "even": even, "squared": squared, "total": total,
		"sorted": sorted, "first_two": xs[:2], "original_first": xs[0], "copied_first": copied[0],
		"score": scores["Ada"], "has_missing": hasMissing, "unique": unique, "parsed": parsed.Active,
		"parsed_integer": number, "error": divisionErr.Error(), "regex": regexp.MustCompile(`^[a-z]+$`).MatchString("hello"),
		"hex": hex.EncodeToString([]byte("hi")), "codepoints": utf8.RuneCountInString("Việt"), "bytes": len("Việt"),
		"big_integer": bigNumber.String(), "date": time.Date(2024, 1, 2, 3, 4, 5, 0, time.UTC).Format(time.RFC3339),
		"file_roundtrip": string(file),
	}
	return json.NewEncoder(os.Stdout).Encode(output)
}
func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
