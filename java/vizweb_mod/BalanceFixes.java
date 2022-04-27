package modification;

import java.awt.Rectangle;
import java.util.List;

import org.vizweb.QuadtreeFeatureComputer;
import org.vizweb.quadtree.Quadtree;
import org.vizweb.quadtree.QuadtreeNode;

//For diagonalBalanceFix
import static com.googlecode.javacv.cpp.opencv_core.cvCountNonZero;

//Tools (static imports for elegance)
import static modification.Tools.*;

/**
 * 
 * @author DanielRibaudo
 * This is a singleton class meant to have several implementations to replace the original Vizweb implementation of quadtree balance.
 * The three main ways are:
 * - Through the original equation from a cited paper
 * - By counting the number of leaf nodes
 * - By adjusting the default vizweb output to prevent NaN from being output
 * 
 * This class may see some refactoring, as some of the code is repetitive.
 * 
 */
public class BalanceFixes {
	
	/**
	 * Gets the number for balance weight, according to the equation: sum_0_i(d_i * a_i) where:
	 * - i is the number of objects in the provided quadtree
	 * - d_i is the distance from the center of object i to the center lines of the image they are in
	 * - a_i is the area of object i
	 * @param root the root node of the quadtree
	 * @param cx the x center of the image
	 * @param cy the y center of the image
	 * @return The balance weight of the provided Quadtree
	 */
	private static double getBalanceEqn(QuadtreeNode root, double cx, double cy) {
		List<QuadtreeNode> leaves = getLeaves(root);
		double sum = 0;
		for (QuadtreeNode leaf : leaves) {
			Rectangle rect = leaf.getROI();
			double area = rect.getWidth() * rect.getHeight();
			area = Math.log(area+1); //Use log, add 1 to prevent negative/infinity
			sum += area*(Math.abs(rect.getCenterX()-cx) + Math.abs(rect.getCenterY()-cy));
		}
		return sum;
	}
	/**
	 * Gets the horizontal balance according to the equation: sum_0_i(d_i * a_i) where:
	 * - i is the number of objects in the provided quadtree
	 * - d_i is the distance from the center of object i to the center lines of the image they are in
	 * - a_i is the area of object i
	 * @param qt The quadtree to calculate horizontal balance for
	 * @return The horizontal balance of the quadtree
	 */
	public static double computeHorizontalBalanceEqn(Quadtree qt) {
		QuadtreeNode root = qt.getRoot();
		QuadtreeNode[] children = getChildrenRefl(root);
		Rectangle rect = root.getROI();
		double cx = rect.getCenterX(), cy = rect.getCenterY();
		return combineWeight(getBalanceEqn(children[0],cx,cy)+getBalanceEqn(children[1],cx,cy), getBalanceEqn(children[2],cx,cy)+getBalanceEqn(children[3],cx,cy));
	}
	/**
	 * Gets the horizontal balance according to the equation: sum_0_i(d_i * a_i) where:
	 * - i is the number of objects in the provided quadtree
	 * - d_i is the distance from the center of object i to the center lines of the image they are in
	 * - a_i is the area of object i
	 * @param qt The quadtree to calculate vertical balance for
	 * @return The vertical balance of the quadtree
	 */
	public static double computeVerticalBalanceEqn(Quadtree qt) {
		QuadtreeNode root = qt.getRoot();
		QuadtreeNode[] children = getChildrenRefl(root);
		Rectangle rect = root.getROI();
		double cx = rect.getCenterX(), cy = rect.getCenterY();
		return combineWeight(getBalanceEqn(children[0],cx,cy)+getBalanceEqn(children[3],cx,cy), getBalanceEqn(children[1],cx,cy)+getBalanceEqn(children[2],cx,cy));
	}
	
	/**
	 * Gets the diagonal balance according to the equation: sum_0_i(d_i * a_i) where:
	 * - i is the number of objects in the provided quadtree
	 * - d_i is the distance from the center of object i to the center lines of the image they are in
	 * - a_i is the area of object i
	 * 
	 * Opposing quadrants both undergo this calculation, and have their weights combined. The average of these two calculations are taken as the result.
	 * @param qt The quadtree to calculate diagonal balance for
	 * @return The diagonal balance of the quadtree
	 */
	public static double computeDiagonalBalanceEqn(Quadtree qt) {
		QuadtreeNode root = qt.getRoot();
		QuadtreeNode[] children = getChildrenRefl(root);
		Rectangle rect = root.getROI();
		double cx = rect.getCenterX(), cy = rect.getCenterY();
		double w1 = combineWeight(getBalanceEqn(children[0],cx,cy), getBalanceEqn(children[2],cx,cy));
		double w2 = combineWeight(getBalanceEqn(children[1],cx,cy), getBalanceEqn(children[3],cx,cy));
		return (w1+w2)/2;
	}
	
	/**
	 * Gets the balance number weight of the provided Quadtree
	 * @param root the root node of the Quadtree
	 * @return The number of leaf nodes in this quadtree
	 */
	private static int getBalanceNum(QuadtreeNode root) {
		return getLeaves(root).size();
	}
	
	/**
	 * Gets the horizontal balance according to how many leaves exist within the tree.
	 * @param qt The quadtree to calculate horizontal balance for
	 * @return The horizontal balance of the tree
	 */
	public static double computeHorizontalBalanceNum(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		return combineWeight(getBalanceNum(children[0])+getBalanceNum(children[1]), getBalanceNum(children[2])+getBalanceNum(children[3]));
	}
	
	/**
	 * Gets the vertical balance according to how many leaves exist wtihin the tree
	 * @param qt The quadtree to calculate vertical balance for
	 * @return The vertical balance of the tree
	 */
	public static double computeVerticalBalanceNum(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		return combineWeight(getBalanceNum(children[0])+getBalanceNum(children[3]), getBalanceNum(children[1])+getBalanceNum(children[2]));
	}
	
	/**
	 * Gets the diagonal balance according to how many leaves exist within the tree
	 * 
	 * Opposing quadrants both undergo this calculation, and have their weights combined. The average of these two calculations are taken as the result.
	 * @param qt The quadtree to calculate diagonal balance for
	 * @return The diagonal balance of the tree
	 */
	public static double computeDiagonalBalanceNum(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		double w1 = combineWeight(getBalanceNum(children[0]), getBalanceNum(children[2]));
		double w2 = combineWeight(getBalanceNum(children[1]), getBalanceNum(children[3]));
		return (w1+w2)/2;
	}
	
	/**
	 * Fixes the result of horizontal balance from the QuadtreeFeatureComputer of Vizweb.
	 * This method cannot return NaN, which is an improvement on the original.
	 * @param qt The quadtree to calculate horizontal balance for
	 * @return The horizontal balance of the tree
	 */
	public static double computeHorizontalBalanceFix(Quadtree qt) {
		double result = QuadtreeFeatureComputer.computeHorizontalBalance(qt);
		return fixNaN(result);
	}
	
	/**
	 * Fixes the result of vertical balance from the quadtree feature computer of Vizweb.
	 * This method cannot return NaN, which is an improvement on the original.
	 * @param qt The quadtree to calculate vertical balance for
	 * @return The vertical balance of the tree
	 */
	public static double computeVerticalBalanceFix(Quadtree qt) {
		double result = QuadtreeFeatureComputer.computeVerticalBalance(qt);
		return fixNaN(result);
	}
	
	/**
	 * Calculates balance as it is originally calculated in Vizweb, but on the diagonals.
	 * Each diagonal is calculated, and the average of the two is returned.
	 * This method cannot return NaN, which is an improvement on the original.
	 * @param qt The quadtree to calculate diagonal balance for
	 * @return The diagonal balance of the quadtree
	 */
	 public static double computeDiagonalBalanceFix(Quadtree qt) {
		QuadtreeNode[] children = getChildrenRefl(qt.getRoot());
		double[] bal = new double[children.length];
		for (int i = 0; i < children.length; ++i) {
			QuadtreeNode child = children[i];
			if (child != null) {
				Quadtree childTree = new Quadtree(child);
				bal[i] = cvCountNonZero(moddedBinaryRepresentation(childTree, -1));
			}
		}
		double w1 = combineWeight(bal[0], bal[2]);
		double w2 = combineWeight(bal[1], bal[3]);
		return (w1+w2)/2;
	 }
	 
	 /**
	  * Computes the average balance using the equation method. Considers horizontal, vertical, and diagonal (radial) balances.
	  * @param qt The quadtree to obtain the average balance of
	  * @return The average balance
	  */
	 public static double computeAverageBalanceEqn(Quadtree qt) {
		 return 1D*(computeHorizontalBalanceEqn(qt)+computeVerticalBalanceEqn(qt)+computeDiagonalBalanceEqn(qt)) / 3;
	 }
	 
	 /**
	  * Computes the average balance using the leaf number method. Considers horizontal, vertical, and diagonal (radial) balances.
	  * @param qt The quadtree to obtain the average balance of
	  * @return The average balance
	  */
	 public static double computeAverageBalanceNum(Quadtree qt) {
		 return 1D*(computeHorizontalBalanceNum(qt)+computeVerticalBalanceNum(qt)+computeDiagonalBalanceNum(qt)) / 3;
	 }
	 
	 /**
	  * Computes the average balance by adjusting the output of the default Vizweb implementation. Considers horizontal, vertical, and diagonal (radial) balances.
	  * @param qt The quadtree to obtain the average balance of
	  * @return The average balance
	  */
	 public static double computeAverageBalanceFix(Quadtree qt) {
		 return 1D*(computeHorizontalBalanceFix(qt)+computeVerticalBalanceFix(qt)+computeDiagonalBalanceFix(qt)) / 3;
	 }
}
