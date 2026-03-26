# Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
# SPDX-License-Identifier: MIT

require_relative 'utils'

RSpec.describe Utils do
  describe '.calculate_average' do
    context 'with valid input' do
      it 'calculates average of single element' do
        expect(Utils.calculate_average([5])).to eq(5.0)
      end

      it 'calculates average of multiple positive numbers' do
        expect(Utils.calculate_average([1, 2, 3, 4, 5])).to eq(3.0)
      end

      it 'calculates average with decimals' do
        expect(Utils.calculate_average([1.5, 2.5, 3.0])).to eq(2.333333333333333)
      end

      it 'calculates average of negative numbers' do
        expect(Utils.calculate_average([-5, -3, -1])).to eq(-3.0)
      end

      it 'calculates average with mixed positive and negative' do
        expect(Utils.calculate_average([-10, 0, 10])).to eq(0.0)
      end

      it 'calculates average with zeros' do
        expect(Utils.calculate_average([0, 0, 0])).to eq(0.0)
      end

      it 'calculates average with large numbers' do
        expect(Utils.calculate_average([1_000_000, 2_000_000, 3_000_000])).to eq(2_000_000.0)
      end

      it 'returns float type' do
        result = Utils.calculate_average([1, 2, 3])
        expect(result).to be_a(Float)
      end
    end

    context 'with edge cases' do
      it 'raises ArgumentError when given an empty array' do
        expect { Utils.calculate_average([]) }.to raise_error(ArgumentError, 'Input must be a non-empty array')
      end

      it 'handles very small numbers' do
        expect(Utils.calculate_average([0.001, 0.002, 0.003])).to be_within(0.0001).of(0.002)
      end

      it 'handles precision with many decimals' do
        result = Utils.calculate_average([1.111, 2.222, 3.333])
        expect(result).to be_within(0.001).of(2.222)
      end
    end

    context 'with invalid input' do
      it 'raises ArgumentError for nil' do
        expect { Utils.calculate_average(nil) }.to raise_error
      end

      it 'raises ArgumentError for non-array input' do
        expect { Utils.calculate_average("not an array") }.to raise_error
      end

      it 'raises error for array with non-numeric values' do
        expect { Utils.calculate_average([1, 2, "three"]) }.to raise_error
      end
    end
  end

  describe '.fizzbuzz' do
    context 'with numbers divisible by both 3 and 5' do
      it 'returns "fizzbuzz" for 15' do
        expect(Utils.fizzbuzz(15)).to eq('fizzbuzz')
      end

      it 'returns "fizzbuzz" for 30' do
        expect(Utils.fizzbuzz(30)).to eq('fizzbuzz')
      end

      it 'returns "fizzbuzz" for 45' do
        expect(Utils.fizzbuzz(45)).to eq('fizzbuzz')
      end

      it 'returns "fizzbuzz" for large multiples of 15' do
        expect(Utils.fizzbuzz(300)).to eq('fizzbuzz')
      end
    end

    context 'with numbers divisible by 3 only' do
      it 'returns "fizz" for 3' do
        expect(Utils.fizzbuzz(3)).to eq('fizz')
      end

      it 'returns "fizz" for 6' do
        expect(Utils.fizzbuzz(6)).to eq('fizz')
      end

      it 'returns "fizz" for 9' do
        expect(Utils.fizzbuzz(9)).to eq('fizz')
      end

      it 'returns "fizz" for large multiples of 3' do
        expect(Utils.fizzbuzz(99)).to eq('fizz')
      end
    end

    context 'with numbers divisible by 5 only' do
      it 'returns "buzz" for 5' do
        expect(Utils.fizzbuzz(5)).to eq('buzz')
      end

      it 'returns "buzz" for 10' do
        expect(Utils.fizzbuzz(10)).to eq('buzz')
      end

      it 'returns "buzz" for 20' do
        expect(Utils.fizzbuzz(20)).to eq('buzz')
      end

      it 'returns "buzz" for large multiples of 5' do
        expect(Utils.fizzbuzz(250)).to eq('buzz')
      end
    end

    context 'with numbers not divisible by 3 or 5' do
      it 'returns the number as string for 1' do
        expect(Utils.fizzbuzz(1)).to eq('1')
      end

      it 'returns the number as string for 2' do
        expect(Utils.fizzbuzz(2)).to eq('2')
      end

      it 'returns the number as string for 4' do
        expect(Utils.fizzbuzz(4)).to eq('4')
      end

      it 'returns the number as string for 7' do
        expect(Utils.fizzbuzz(7)).to eq('7')
      end

      it 'returns the number as string for large numbers' do
        expect(Utils.fizzbuzz(101)).to eq('101')
      end
    end

    context 'with zero and negative numbers' do
      it 'returns "fizzbuzz" for zero' do
        expect(Utils.fizzbuzz(0)).to eq('fizzbuzz')
      end

      it 'returns "fizz" for negative multiple of 3' do
        expect(Utils.fizzbuzz(-3)).to eq('fizz')
      end

      it 'returns "buzz" for negative multiple of 5' do
        expect(Utils.fizzbuzz(-5)).to eq('buzz')
      end

      it 'returns "fizzbuzz" for negative multiple of 15' do
        expect(Utils.fizzbuzz(-15)).to eq('fizzbuzz')
      end

      it 'returns negative number as string' do
        expect(Utils.fizzbuzz(-7)).to eq('-7')
      end
    end

    context 'with large numbers' do
      it 'handles large numbers correctly' do
        expect(Utils.fizzbuzz(1_000_000)).to eq('buzz')
      end

      it 'handles large fizzbuzz case' do
        expect(Utils.fizzbuzz(999_999)).to eq('fizzbuzz')
      end
    end
  end

  describe '.reverse_words' do
    context 'with valid sentences' do
      it 'reverses words in a simple sentence' do
        expect(Utils.reverse_words('hello world')).to eq('world hello')
      end

      it 'reverses words in a three-word sentence' do
        expect(Utils.reverse_words('one two three')).to eq('three two one')
      end

      it 'reverses words with longer sentence' do
        expect(Utils.reverse_words('the quick brown fox')).to eq('fox brown quick the')
      end

      it 'handles single word' do
        expect(Utils.reverse_words('hello')).to eq('hello')
      end

      it 'preserves word case' do
        expect(Utils.reverse_words('Hello World')).to eq('World Hello')
      end

      it 'handles mixed case words' do
        expect(Utils.reverse_words('ThE QuiCk BroWn')).to eq('BroWn QuiCk ThE')
      end
    end

    context 'with whitespace handling' do
      it 'strips leading whitespace' do
        expect(Utils.reverse_words('  hello world')).to eq('world hello')
      end

      it 'strips trailing whitespace' do
        expect(Utils.reverse_words('hello world  ')).to eq('world hello')
      end

      it 'strips both leading and trailing whitespace' do
        expect(Utils.reverse_words('  hello world  ')).to eq('world hello')
      end

      it 'handles multiple spaces between words' do
        expect(Utils.reverse_words('hello    world')).to eq('world hello')
      end

      it 'handles tabs and various whitespace' do
        expect(Utils.reverse_words('hello\tworld')).to eq('world hello')
      end

      it 'handles mixed whitespace characters' do
        expect(Utils.reverse_words('hello  \t  world')).to eq('world hello')
      end

      it 'handles newlines and whitespace' do
        expect(Utils.reverse_words("hello\nworld")).to eq('world hello')
      end
    end

    context 'with edge cases' do
      it 'handles empty string' do
        expect(Utils.reverse_words('')).to eq('')
      end

      it 'handles string with only whitespace' do
        expect(Utils.reverse_words('   ')).to eq('')
      end

      it 'handles string with tabs only' do
        expect(Utils.reverse_words("\t\t\t")).to eq('')
      end

      it 'handles single character word' do
        expect(Utils.reverse_words('a b c')).to eq('c b a')
      end

      it 'handles words with punctuation' do
        expect(Utils.reverse_words('hello, world!')).to eq('world! hello,')
      end

      it 'handles words with numbers' do
        expect(Utils.reverse_words('hello 123 world')).to eq('world 123 hello')
      end

      it 'handles special characters' do
        expect(Utils.reverse_words('@home #world')).to eq('#world @home')
      end
    end

    context 'with unicode and special strings' do
      it 'handles unicode characters' do
        expect(Utils.reverse_words('café naïve')).to eq('naïve café')
      end

      it 'handles emoji' do
        expect(Utils.reverse_words('👋 🌍')).to eq('🌍 👋')
      end

      it 'handles mixed unicode and regular text' do
        expect(Utils.reverse_words('hello 🌍 world')).to eq('world 🌍 hello')
      end

      it 'handles words with hyphens' do
        expect(Utils.reverse_words('well-known public-domain')).to eq('public-domain well-known')
      end
    end

    context 'with long sentences' do
      it 'handles long sentence' do
        input = 'the quick brown fox jumps over the lazy dog'
        expected = 'dog lazy the over jumps fox brown quick the'
        expect(Utils.reverse_words(input)).to eq(expected)
      end

      it 'handles sentence with many repeated words' do
        input = 'a a a b b c'
        expected = 'c b b a a a'
        expect(Utils.reverse_words(input)).to eq(expected)
      end
    end

    context 'return type' do
      it 'returns a string' do
        result = Utils.reverse_words('hello world')
        expect(result).to be_a(String)
      end
    end
  end
end
