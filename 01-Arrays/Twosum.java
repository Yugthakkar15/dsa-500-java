import java.util.*;

public class Twosum {
    public int[] twosum(int nums[], int target) {
        int n = nums.length;
        HashMap<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int ans = target - nums[i];
            if (map.containsKey(ans)) {
                return new int[] { map.get(ans), i };

            } else {
                map.put(nums[i], i);
            }
        }
        return new int[] {};
    }

    public static void main(String[] args) {
        int[] nums = { 2, 7, 11, 15 };
        int target = 9;
        Twosum a = new Twosum();
        a.twosum(nums, target);
    }
}
