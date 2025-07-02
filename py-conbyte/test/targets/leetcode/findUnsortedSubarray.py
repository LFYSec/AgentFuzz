
def findUnsortedSubarray(nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    stack = []
    l, r = len(nums), 0
    for i in range(len(nums)):
        while len(stack) != 0 and nums[stack[-1]] > nums[i]:
            l = min(l, stack.pop())
        stack.append(i)
    stack = []
    for i in range(len(nums) - 1, -1, -1):
        while len(stack) != 0 and nums[stack[-1]] < nums[i]:
            r = max(r, stack.pop())
        stack.append(i)
    if r > l:
        return r - l + 1
    return 0
