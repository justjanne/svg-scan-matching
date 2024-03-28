export default {
  multipass: true,
  js2svg: {
    indent: 4,
    pretty: true,
  },
  plugins: [
    "removeMetadata",
    {
      name: "convertTransform",
      params: {
        removeUseless: true,
        collapseIntoOne: true,
      },
    },
    'removeEditorsNSData',
    'moveGroupAttrsToElems',
    'convertShapeToPath',
    'convertStyleToAttrs',
    'removeOffCanvasPaths',
    'removeRasterImages',
    'removeUselessStrokeAndFill',
    'mergePaths',
    {
      name: "convertPathData",
      params: {
        applyTransforms: true,
        applyTransformsStroked: true,
        forceAbsolutePath: true,
        straightCurves: true,
        lineShorthands: true,
        removeUseless: true,
        collapseRepeated: true,
        negativeExtraSpace: false,
        makeArcs: false
      },
    },
    {
      name: "removeAttrs",
      params: {
        attrs: ["fill", "stroke", "style"],
        elemSeparator: ":",
        preserveCurrentColor: false
      }
    }
  ],
};
