import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Typography } from "@material-ui/core";

export default function Pipelines({ pipelines }) {
  return (
    <>
      <Typography variant="h6">Pipelines</Typography>
      <List>
        {pipelines.map((p) => (
          <ListItem key={p.id}>
            <ListItemText primary={p.name} />
          </ListItem>
        ))}
      </List>
    </>
  );
}

export async function getServerSideProps(context) {
  const res = await fetch("http://rest:3000/pipeline");
  const pipelines = await res.json();

  return {
    props: {
      pipelines,
    },
  };
}
