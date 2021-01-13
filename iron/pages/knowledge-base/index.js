import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Typography } from "@material-ui/core";

export default function KB({ kbs }) {
  return (
    <>
      <Typography variant="h6">Knowledge Bases</Typography>
      <List>
        {kbs.map((k, i) => (
          <ListItem key={k.id} divider={i < kbs.length - 1}>
            <ListItemText primary={k.name} />
          </ListItem>
        ))}
      </List>
    </>
  );
}

export async function getServerSideProps(context) {
  const res = await fetch("http://rest:3000/knowledge-base");
  const kbs = await res.json();

  return {
    props: {
      kbs,
    },
  };
}
