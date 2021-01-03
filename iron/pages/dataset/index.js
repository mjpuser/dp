import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Typography } from "@material-ui/core";

export default function About({ datasets }) {
  return (
    <>
      <Typography variant="h6">Datasets</Typography>
      <List>
        {datasets.map((d, i) => (
          <ListItem key={d.id} divider={i < datasets.length - 1}>
            <ListItemText primary={d.name} />
          </ListItem>
        ))}
      </List>
    </>
  );
}

export async function getServerSideProps(context) {
  const res = await fetch("http://rest:3000/dataset");
  const datasets = await res.json();

  return {
    props: {
      datasets,
    },
  };
}
