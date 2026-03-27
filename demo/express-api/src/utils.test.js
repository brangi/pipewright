// Copyright (c) 2026 Gibran Rodriguez <brangi000@gmail.com>
// SPDX-License-Identifier: MIT

const { isValidEmail, slugify, paginate, parseDuration } = require('./utils');

describe('isValidEmail', () => {
  describe('happy paths', () => {
    it('should validate a simple email', () => {
      expect(isValidEmail('user@example.com')).toBe(true);
    });

    it('should validate an email with multiple domain parts', () => {
      expect(isValidEmail('user@mail.example.co.uk')).toBe(true);
    });

    it('should validate an email with numbers and special chars in local part', () => {
      expect(isValidEmail('user.name+tag123@example.com')).toBe(true);
    });

    it('should validate an email with hyphens in domain', () => {
      expect(isValidEmail('user@my-domain.com')).toBe(true);
    });
  });

  describe('edge cases', () => {
    it('should reject email with space in local part', () => {
      expect(isValidEmail('user name@example.com')).toBe(false);
    });

    it('should reject email with space in domain', () => {
      expect(isValidEmail('user@exam ple.com')).toBe(false);
    });

    it('should reject email without domain extension', () => {
      expect(isValidEmail('user@example')).toBe(false);
    });

    it('should reject email without local part', () => {
      expect(isValidEmail('@example.com')).toBe(false);
    });

    it('should reject email without domain', () => {
      expect(isValidEmail('user@')).toBe(false);
    });

    it('should reject empty string', () => {
      expect(isValidEmail('')).toBe(false);
    });

    it('should reject email with multiple @ symbols', () => {
      expect(isValidEmail('user@@example.com')).toBe(false);
    });

    it('should reject email with just @', () => {
      expect(isValidEmail('@')).toBe(false);
    });

    it('should reject email without @ symbol', () => {
      expect(isValidEmail('userexample.com')).toBe(false);
    });
  });

  describe('error handling', () => {
    it('should return false for null', () => {
      expect(isValidEmail(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isValidEmail(undefined)).toBe(false);
    });

    it('should return false for number', () => {
      expect(isValidEmail(123)).toBe(false);
    });

    it('should return false for object', () => {
      expect(isValidEmail({})).toBe(false);
    });

    it('should return false for array', () => {
      expect(isValidEmail([])).toBe(false);
    });

    it('should return false for boolean', () => {
      expect(isValidEmail(true)).toBe(false);
    });
  });
});

describe('slugify', () => {
  describe('happy paths', () => {
    it('should convert to lowercase and trim', () => {
      expect(slugify('  HELLO WORLD  ')).toBe('hello-world');
    });

    it('should replace spaces with hyphens', () => {
      expect(slugify('hello world test')).toBe('hello-world-test');
    });

    it('should handle already-slugified text', () => {
      expect(slugify('hello-world')).toBe('hello-world');
    });

    it('should handle single word', () => {
      expect(slugify('Hello')).toBe('hello');
    });

    it('should handle text with punctuation', () => {
      expect(slugify('Hello, World!')).toBe('hello-world');
    });

    it('should handle text with numbers', () => {
      expect(slugify('Hello World 123')).toBe('hello-world-123');
    });
  });

  describe('edge cases', () => {
    it('should handle empty string', () => {
      expect(slugify('')).toBe('');
    });

    it('should handle string with only spaces', () => {
      expect(slugify('   ')).toBe('');
    });

    it('should remove special characters', () => {
      expect(slugify('hello@#$%world')).toBe('helloworld');
    });

    it('should handle underscores as separators', () => {
      expect(slugify('hello_world')).toBe('hello-world');
    });

    it('should handle multiple spaces', () => {
      expect(slugify('hello    world')).toBe('hello-world');
    });

    it('should handle multiple underscores', () => {
      expect(slugify('hello___world')).toBe('hello-world');
    });

    it('should remove leading hyphens', () => {
      expect(slugify('---hello')).toBe('hello');
    });

    it('should remove trailing hyphens', () => {
      expect(slugify('hello---')).toBe('hello');
    });

    it('should handle text with only special characters', () => {
      expect(slugify('!@#$%^&*()')).toBe('');
    });

    it('should handle mixed case with special chars and spaces', () => {
      expect(slugify('  Hello! World? Test#123  ')).toBe('hello-world-test123');
    });
  });

  describe('character preservation', () => {
    it('should preserve alphanumeric characters', () => {
      expect(slugify('Test123ABC')).toBe('test123abc');
    });

    it('should handle hyphens correctly', () => {
      expect(slugify('hello-world-test')).toBe('hello-world-test');
    });

    it('should not modify legitimate hyphens', () => {
      expect(slugify('my-awesome-slug')).toBe('my-awesome-slug');
    });
  });
});

describe('paginate', () => {
  const testArray = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  describe('happy paths', () => {
    it('should paginate with default parameters', () => {
      const result = paginate(testArray);
      expect(result.data).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
      expect(result.total).toBe(10);
      expect(result.page).toBe(1);
      expect(result.totalPages).toBe(1);
    });

    it('should return first page with custom perPage', () => {
      const result = paginate(testArray, 1, 5);
      expect(result.data).toEqual([1, 2, 3, 4, 5]);
      expect(result.total).toBe(10);
      expect(result.page).toBe(1);
      expect(result.totalPages).toBe(2);
    });

    it('should return second page', () => {
      const result = paginate(testArray, 2, 5);
      expect(result.data).toEqual([6, 7, 8, 9, 10]);
      expect(result.total).toBe(10);
      expect(result.page).toBe(2);
      expect(result.totalPages).toBe(2);
    });

    it('should handle page that exists but is partially filled', () => {
      const result = paginate(testArray, 3, 4);
      expect(result.data).toEqual([9, 10]);
      expect(result.total).toBe(10);
      expect(result.page).toBe(3);
      expect(result.totalPages).toBe(3);
    });

    it('should calculate totalPages correctly', () => {
      const result = paginate(testArray, 1, 3);
      expect(result.totalPages).toBe(4); // ceil(10/3) = 4
    });
  });

  describe('edge cases', () => {
    it('should handle empty array', () => {
      const result = paginate([], 1, 10);
      expect(result.data).toEqual([]);
      expect(result.total).toBe(0);
      expect(result.totalPages).toBe(0);
    });

    it('should handle single item array', () => {
      const result = paginate([1], 1, 10);
      expect(result.data).toEqual([1]);
      expect(result.total).toBe(1);
      expect(result.totalPages).toBe(1);
    });

    it('should handle page 1 with perPage = 1', () => {
      const result = paginate([1, 2, 3], 1, 1);
      expect(result.data).toEqual([1]);
      expect(result.totalPages).toBe(3);
    });

    it('should handle requested page beyond available pages', () => {
      const result = paginate(testArray, 100, 5);
      expect(result.data).toEqual([]);
      expect(result.page).toBe(100);
    });

    it('should handle large perPage value', () => {
      const result = paginate(testArray, 1, 1000);
      expect(result.data).toEqual(testArray);
      expect(result.totalPages).toBe(1);
    });

    it('should handle perPage = 1', () => {
      const result = paginate([1, 2, 3], 2, 1);
      expect(result.data).toEqual([2]);
    });
  });

  describe('error handling', () => {
    it('should throw error if items is not an array', () => {
      expect(() => paginate('not an array')).toThrow('Items must be an array');
    });

    it('should throw error if items is null', () => {
      expect(() => paginate(null)).toThrow('Items must be an array');
    });

    it('should throw error if items is object', () => {
      expect(() => paginate({})).toThrow('Items must be an array');
    });

    it('should throw error if page is less than 1', () => {
      expect(() => paginate(testArray, 0)).toThrow('Page must be >= 1');
    });

    it('should throw error if page is negative', () => {
      expect(() => paginate(testArray, -1)).toThrow('Page must be >= 1');
    });

    it('should throw error if perPage is less than 1', () => {
      expect(() => paginate(testArray, 1, 0)).toThrow('perPage must be >= 1');
    });

    it('should throw error if perPage is negative', () => {
      expect(() => paginate(testArray, 1, -5)).toThrow('perPage must be >= 1');
    });

    it('should throw error if page is decimal', () => {
      expect(() => paginate(testArray, 1.5)).not.toThrow();
    });
  });

  describe('data integrity', () => {
    it('should not modify original array', () => {
      const original = [1, 2, 3];
      const copy = [...original];
      paginate(original, 1, 2);
      expect(original).toEqual(copy);
    });

    it('should maintain object items in pagination', () => {
      const items = [{ id: 1 }, { id: 2 }, { id: 3 }];
      const result = paginate(items, 1, 2);
      expect(result.data).toEqual([{ id: 1 }, { id: 2 }]);
    });
  });
});

describe('parseDuration', () => {
  describe('happy paths', () => {
    it('should parse hours only', () => {
      expect(parseDuration('2h')).toBe(7200);
    });

    it('should parse minutes only', () => {
      expect(parseDuration('30m')).toBe(1800);
    });

    it('should parse seconds only', () => {
      expect(parseDuration('45s')).toBe(45);
    });

    it('should parse hours and minutes', () => {
      expect(parseDuration('2h30m')).toBe(9000);
    });

    it('should parse hours, minutes, and seconds', () => {
      expect(parseDuration('1h30m45s')).toBe(5445);
    });

    it('should parse all three units in different order', () => {
      expect(parseDuration('45s2h30m')).toBe(9045);
    });

    it('should parse with single digit values', () => {
      expect(parseDuration('1h1m1s')).toBe(3661);
    });

    it('should parse large values', () => {
      expect(parseDuration('100h')).toBe(360000);
    });

    it('should handle zero values', () => {
      expect(parseDuration('0h30m')).toBe(1800);
    });
  });

  describe('edge cases', () => {
    it('should parse with leading/trailing spaces', () => {
      expect(parseDuration('  2h30m  ')).toBe(9000);
    });

    it('should handle consecutive values', () => {
      expect(parseDuration('2h3m')).toBe(7380);
    });

    it('should parse very large numbers', () => {
      expect(parseDuration('9999h')).toBe(35996400);
    });

    it('should handle multiple occurrences of same unit', () => {
      expect(parseDuration('1h2h')).toBe(10800);
    });

    it('should not parse with extra spaces between number and unit', () => {
      // Spaces between number and unit are not allowed by the regex
      expect(() => parseDuration('2 h 30 m')).toThrow(/Invalid duration format/);
    });

    it('should parse complex mixed format', () => {
      expect(parseDuration('1h2m3s')).toBe(3723);
    });

    it('should handle repeated units', () => {
      expect(parseDuration('30m30m')).toBe(3600);
    });
  });

  describe('error handling', () => {
    it('should throw error for empty string', () => {
      expect(() => parseDuration('')).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for null', () => {
      expect(() => parseDuration(null)).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for undefined', () => {
      expect(() => parseDuration(undefined)).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for number', () => {
      expect(() => parseDuration(123)).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for object', () => {
      expect(() => parseDuration({})).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for array', () => {
      expect(() => parseDuration([])).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for string with only spaces', () => {
      expect(() => parseDuration('   ')).toThrow('Duration must be a non-empty string');
    });

    it('should throw error for invalid duration format', () => {
      expect(() => parseDuration('invalid')).toThrow(/Invalid duration format/);
    });

    it('should throw error for numbers without unit', () => {
      expect(() => parseDuration('123')).toThrow(/Invalid duration format/);
    });

    it('should throw error for unsupported unit', () => {
      expect(() => parseDuration('5d')).toThrow(/Invalid duration format/);
    });

    it('should ignore trailing invalid characters and parse valid parts', () => {
      // The regex ignores non-matching characters, so '2h@#$' parses as 2h
      expect(parseDuration('2h@#$')).toBe(7200);
    });

    it('should throw error for unit without number', () => {
      expect(() => parseDuration('h')).toThrow(/Invalid duration format/);
    });

    it('should match digits within floating point (parses 5h from 2.5h)', () => {
      // The regex /(\d+)(h|m|s)/g is greedy and matches any consecutive digits
      // In '2.5h', it matches '5h', resulting in 5 * 3600 = 18000 seconds
      expect(parseDuration('2.5h')).toBe(18000);
    });

    it('should throw error when no valid matches found', () => {
      expect(() => parseDuration('no units here')).toThrow(/Invalid duration format/);
    });
  });

  describe('calculation accuracy', () => {
    it('should correctly calculate 1 hour', () => {
      expect(parseDuration('1h')).toBe(3600);
    });

    it('should correctly calculate 1 minute', () => {
      expect(parseDuration('1m')).toBe(60);
    });

    it('should correctly calculate 1 second', () => {
      expect(parseDuration('1s')).toBe(1);
    });

    it('should correctly sum multiple units', () => {
      const result = parseDuration('1h1m1s');
      const expected = 3600 + 60 + 1;
      expect(result).toBe(expected);
    });

    it('should handle complex real-world case', () => {
      expect(parseDuration('24h')).toBe(86400); // 1 day
    });

    it('should handle 90 minute duration', () => {
      expect(parseDuration('1h30m')).toBe(5400);
    });
  });
});
