import LensIcon from "@material-ui/icons/Lens";
import React from "react";
import Tree from "react-d3-tree";

export default function NewPipeline() {
  const graph = {
    name: "root",
    children: [
        {name: 'transform 1'},
        {name: 'transform 2'}
    ],
  };
  return (
    <div id="treeWrapper" style={{ width: "100%", height: "100vh" }}>
      New Pipeline
      <Tree zoomable={false} translate={{x: 200, y: 300 }} data={graph} />
    </div>
  );
}
