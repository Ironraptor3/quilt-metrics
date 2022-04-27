package modification;

import java.awt.Rectangle;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

import org.vizweb.quadtree.Quadtree;
import org.vizweb.quadtree.QuadtreeNode;

import com.googlecode.javacv.cpp.opencv_core.CvPoint;
import com.googlecode.javacv.cpp.opencv_core.IplImage;
import static com.googlecode.javacv.cpp.opencv_core.CV_FILLED;
import static com.googlecode.javacv.cpp.opencv_core.cvPoint;
import static com.googlecode.javacv.cpp.opencv_core.cvRectangle;
import static com.googlecode.javacv.cpp.opencv_core.cvScalar;
import static com.googlecode.javacv.cpp.opencv_core.cvScalarAll;
import static com.googlecode.javacv.cpp.opencv_core.cvSize;
import static com.googlecode.javacv.cpp.opencv_core.cvSet;
/**
 * 
 * @author DanielRibaudo
 * A singleton tools class for other classes to use.
 */
public class Tools {
	// Each of the node fields to get via reflexivity, arranged in quadrant order
	private static String[] nodes = {"q1", "q2", "q3", "q4"};
	/**
	 * Uses reflection to get the child nodes of a QuadtreeNode.
	 * @param root The QuadtreeNode to get the children of
	 * @return An array of the children (null if they do not exist, an error/exception occurs, or the root is null)
	 */
	public static QuadtreeNode[] getChildrenRefl(QuadtreeNode root) {
		QuadtreeNode result[] = new QuadtreeNode[nodes.length];
		if (root != null) {
			for (int i = 0; i < nodes.length; ++i) {
				String node = nodes[i];
				try {
					Field f = root.getClass().getDeclaredField(node);
					f.setAccessible(true);
					result[i] = (QuadtreeNode) f.get(root);
				} catch (SecurityException e) {
					e.printStackTrace();
				} catch (NoSuchFieldException e) {
					e.printStackTrace();
				} catch (IllegalArgumentException e) {
					e.printStackTrace();
				} catch (IllegalAccessException e) {
					e.printStackTrace();
				}
			}
		}
		return result;
	}
	/**
	 * Whilst performing these operations, 1 - 0/0 may be encountered. This causes the default implementation to return NaN.
	 * This is not a desirable result, and NaN is therefore treated as 1 (as both sides are 0, which means the sides are 100% balanced)
	 * @param d The double to fix
	 * @return 1 if d is NaN, d otherwise
	 */
	public static double fixNaN(double d) {
		if (Double.isNaN(d)) {
			d = 1;
		}
		return d;
	}
	
	/**
	 * Balance combining equation. 1 - |w1 - w2 | / max(w1, w2).
	 * @param w1 The first weight
	 * @param w2 The second weight
	 * @return How similar the two weights are. Approaches 1 as w1 and w2 get relatively closer. As expected, returns 1 if both are 0.
	 */
	public static double combineWeight(double w1, double w2) {
		double result = 1D - (Math.abs(w1-w2) / Math.max(w1, w2)); //1 (or NAN) if w1 = w2
		return fixNaN(result);
	}
	/**
	 * Returns a list of all leaf nodes in the provided QuadTree
	 * @param root the root node of the Quadtree
	 * @return A list of all leaf nodes in this tree. An empty list will be returned if the provided root is null.
	 */
	public static List<QuadtreeNode> getLeaves(QuadtreeNode root) {
		List<QuadtreeNode> leaves = new ArrayList<QuadtreeNode>();
		return root==null?leaves:getLeavesHelper(root, leaves);
	}
	
	/**
	 * Helper method for get leaves. Recursively finds all leaf nodes.
	 * @param root the root node of the Quadtree
	 * @param leaves a list to add leaves to
	 * @return The list of leaves provided in the parameters, for chaining.
	 */
	private static List<QuadtreeNode> getLeavesHelper(QuadtreeNode root, List<QuadtreeNode> leaves) {
		boolean isLeaf = true;

		for (QuadtreeNode child : getChildrenRefl(root)) {
			if (child != null) {
				getLeavesHelper(child, leaves);
				isLeaf = false;
			}
		}

		if (isLeaf) {
			leaves.add(root);
		}
		return leaves;
	}
	
	/**
	 * Calling createBinaryRepresentation on a Quadtree child is not allowed.
	 * It results in undefined behavior.
	 * This modification allows the function to be called on any Quadtree
	 * @param qt The quadtree to create a binary representation of
	 * @param size -1 to paint each layer, or a positive number to specify the max size of leaf to draw
	 * @return The binary representation of the Quadtree
	 */
	public static IplImage moddedBinaryRepresentation(Quadtree qt, int size) {
		if (qt != null) {
			QuadtreeNode root = qt.getRoot();
			IplImage bin = IplImage.create(cvSize(root.getROI().width, root.getROI().height), 8, 1);
			cvSet(bin, cvScalarAll(0), null);
			moddedPainter(bin, size, root, root);
			return bin;
		}
		else {
			return null;
		}
	}

	/**
	 * Helper function for moddedBinaryRepresentation that draws recursively
	 * @param bin The binary image to draw to
	 * @param size size -1 to paint each layer, or a positive number to specify the max size of leaf to draw
	 * @param root The original root for offset purposes
	 * @param node The current node being considered/drawn
	 */
	private static void moddedPainter(IplImage bin, int size, QuadtreeNode root, QuadtreeNode node) {
		if (node == null) {
			return;
		}
		Rectangle rootROI = root.getROI(),
				nodeROI = node.getROI();
		
		int x = nodeROI.x-rootROI.x,
				y = nodeROI.y-rootROI.y;

		CvPoint p1 = cvPoint(x,y),
				p2 = cvPoint(x+nodeROI.width, y+nodeROI.height);

		if (size > 0) { //Leaf implementation
			if (nodeROI.width < size || nodeROI.height < size) {
				cvRectangle(bin, p1, p2, cvScalarAll(255), CV_FILLED, 8, 0);
				return; //Skip further recursion, it is already painted
			}
		}
		else { // Default Implementation
			cvRectangle(bin, p1, p2, cvScalar(255,255,20,20), 1, 8, 0);
		}
		for (QuadtreeNode child : getChildrenRefl(node)) {
			moddedPainter(bin, size, root, child);
		}
	}
}
