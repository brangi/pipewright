# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

# Simple utility functions for testing pipewright's test-gen workflow.
module Utils
  # Calculate the average of an array of numbers.
  # Raises ArgumentError if the array is empty.
  def self.calculate_average(numbers)
    raise ArgumentError, "Input must be a non-empty array" if numbers.empty?

    numbers.sum.to_f / numbers.length
  end

  # Return "fizz", "buzz", "fizzbuzz", or the number as a string.
  def self.fizzbuzz(n)
    if (n % 15).zero?
      "fizzbuzz"
    elsif (n % 3).zero?
      "fizz"
    elsif (n % 5).zero?
      "buzz"
    else
      n.to_s
    end
  end

  # Reverse the order of words in a sentence.
  def self.reverse_words(sentence)
    sentence.strip.split(/\s+/).reverse.join(" ")
  end
end
