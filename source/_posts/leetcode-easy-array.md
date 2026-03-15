---
title: "LeetCode初级算法-数组篇"
tags:
   - Algorithm
categories:
   - 基础夯实
date: 2021-08-07 10:36
description: "LeetCode初级算法数组篇题解，包含删除重复项、旋转数组、两数之和等经典题目的解题思路。"
---

[点击查看题目网址](https://leetcode-cn.com/explore/featured/card/top-interview-questions-easy/1/array/)

### 重复相关

##### 1. 删除排序数组的重复项

> 这个主要要求**原地**删除，不使用额外的数组空间，使用O(1)的额外空间

这个题主要可以用双指针法来确定。一个用于遍历数组，记为i；另一个用于记录不重复数组的最后的位置，记为count；其中count和i相互操作用于替换

即：

> 1   2   2  3  4
>   count  i

比较的是count-1和 i

```java
    public int removeDuplicates(int[] nums) {
        int count = 1;
        for(int i = 1; i < nums.length; i++){
            if (nums[count - 1] != nums[i]){
                nums[count] = nums[i];
                count++;
            }
        }
        return count;
    }
```

第六个也是用的双指针

##### 2.  存在重复元素

* 方法一：先排序，然后再查找重复元素

  ```java
  public boolean containsDuplicate(int[] nums) {
          Arrays.sort(nums);
          for (int i = 0; i < nums.length; i ++){
              if (nums[i] == nums[i + 1]){
                  return true;
              }
          }
          return false;
      }
  ```

* 方法二：利用Set集合的不重复性来实现查找重复元素

  ```java
      public boolean containsDuplicate(int[] nums) {
          Set<Integer> set = new HashSet<>(nums.length);
          for(int num: nums){
              if (set.contains(num)){
                  return true;
              }
              set.add(num);
          }
          return false;
      }
  ```

##### 3. 只出现一次的数字

>  可以利用异或的特性：

* 1 ^ 1 = 0
* 0 ^ 1 = 1

```java
    public int singleNumber(int[] nums) {
         int singleNumber = 0;
        for (int num : nums) {
            singleNumber ^= num;
        }
        return singleNumber;
    }
```

##### 4. 买股票的最佳时机 贰

> 其实就是问的**两数之差的和的最大值**，其中，大的数要在小的数后面

```java
    public int maxProfit(int[] prices) {
        int maxprofit = 0;
        for (int i = 1; i < prices.length; i++) {
            if (prices[i] > prices[i - 1])
                maxprofit += prices[i] - prices[i - 1];
        }
        return maxprofit;
    }
```

### 数组移动相关

##### 5. 旋转数组

```java
    public void rotate(int[] nums, int k) {
        int temp;
        int length = nums.length;
        k %= length;
        for(int j = 0; j < k; j++){
            // 把最后一个存入temp中
            temp = nums[length - 1];
            // 把数组内容往右移
            for(int i = length - 1; i > 0; i--){
                nums[i] = nums[i - 1];
            }
            // 把最后的数据移动到第一个
            nums[0] = temp;
        }
    }
```

##### 6. 移动零

> 需要2个指针，第一个指向0（需要不断检测），第二个指向非0

* 0		1		0		3		12
  i         j
* 1		0		0		3		12
     		i		    	    j
* 1        3         0        0        12
                                        i 				  j        

```java
public void moveZeroes(int[] nums) {
        // i 代表0的位置，j 代表0之后非0的位置
        for (int i = 0, j = 0; i < nums.length && j < nums.length;){
            // 如果i指针为0
            if (nums[i] == 0){
                // 且j指针不为0
                if (nums[j] != 0){
                    // 交换i和j，且i和j均++
                    nums[i ++] = nums[j];
                    nums[j ++] = 0; 
                // j指针为0，则i不动，j++
                } else {
                    j ++;
                }
            // i指针不为0，i和j均++
            } else {
                i ++;
                j ++;
            }
        }
    }
```

##### 7. 加一

有三种情况：

* $$
  123 \rightarrow 124
  $$

* $$
  1299 \rightarrow 1300
  $$

* $$
  999 \rightarrow 1000
  $$

```java
    public int[] plusOne(int[] digits) {
        // 循环是为了解决譬如 1299的问题
        for (int i = digits.length - 1; i > -1; i --){
            digits[i] ++;
            digits[i] %= 10;
            // 如果所有循环都不能到达if，那么数组元素必定都为0
            if (digits[i] != 0){
                return digits;
            }
        }
        // 为了解决譬如 999 的问题
        digits = new int[digits.length + 1];
        digits[0] = 1;
        return digits;
    }
```

### 两个数组

##### 8. 两个数组的交集 贰

正常来说，这个题能想到的有两种方法：

* 用map存第一个数组，然后拿出来和第二个数组比对

* 先排序，然后用双指针

  ```java
  public int[] intersect(int[] nums1, int[] nums2) {
  
          int [] outTemp = new int[nums1.length > nums2.length ? nums2.length : nums1.length];
          int temp = 0;
  
          Arrays.sort(nums1);
          Arrays.sort(nums2);
  
          for (int i1 = 0, i2 = 0; i1 < nums1.length && i2 < nums2.length;){
              if (nums1[i1] == nums2[i2]){
                  outTemp[temp ++] = nums1[i1];
                  i2 ++;
                  i1 ++;
              } else if (nums1[i1] > nums2[i2]){
                  i2 ++;
              } else if (nums1[i1] < nums2[i2]){
                  i1 ++;
              }
          }
          return Arrays.copyOfRange(outTemp, 0, temp);
      }
  ```

##### 9. 两数之和 

这个题比较巧的就是用了map，譬如

nums = 2,7,8,12  target = 9

我们要注意：9 - 7 = 2 ,同时 9 - 2 = 7

```java
public int[] twoSum(int[] nums, int target) {
        int[] twoSum = new int[2];
        HashMap<Integer,Integer> hashMap = new HashMap<>(100);
        for (int i = 0; i < nums.length; i++) {
            int component = target - nums[i];
            if (hashMap.containsKey(component)){
                twoSum[0] = i;
                twoSum[1] = hashMap.get(component);
                break;
            }
            // 如果不包含，就把它放进map中
            hashMap.put(nums[i],i);
        }
        return twoSum;
    }
```

### 二维数组

##### 10. 有效的数独

这道题比较秀的一点是，它利用了三个set来存放row，column和box，同时9个box的索引可以通过`(row / 3 ) * 3 + column / 3`

```java
    public boolean isValidSudoku(char[][] board) {

        Set<Character> [] rows = new HashSet[9];
        Set<Character> [] columns = new HashSet[9];
        Set<Character> [] boxes = new HashSet[9];
        
        for (int i = 0; i < 9; i ++){
            rows[i] = new HashSet<>(9);
            columns[i] = new HashSet<>(9);
            boxes[i] = new HashSet<>(9);
        }
        
        for (int i = 0; i < 9; i ++){
            for (int j = 0; j < 9; j ++){
                char num = board[i][j];
                int boxIndex = (i / 3 ) * 3 + j / 3;
                if ((rows[i].contains(num) || columns[j].contains(num) || boxes[boxIndex].contains(num)) && num != '.'){
                    return false;
                }
                rows[i].add(num);
                columns[j].add(num);
                boxes[boxIndex].add(num);
            }
        }
        return true;
    }
```

##### 11. 旋转图像

这道题用到了 转置 + 翻转 的线性代数中的特性
$$
[
  [1,2,3],
  [4,5,6],    
  [7,8,9]
]
\rightarrow 
[
  [1,4,7],
  [2,5,8],    
  [3,6,9]
]
\rightarrow 
[
  [7,4,1],
  [8,5,2],    
  [9,6,3]
]
$$

```java
 public void rotate(int[][] matrix) {
        int length = matrix.length;
        int temp;
        for (int i = 0; i < length; i ++){
            for (int j = i; j < length; j ++){
                temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp;
            }
        }
        
        for (int i = 0; i < length; i ++){
            for (int j = 0; j < length / 2; j ++){
                temp = matrix[i][j];
                matrix[i][j] = matrix[i][length - j - 1];
                matrix[i][length - j -1] = temp;
            }
        }
    }
```



