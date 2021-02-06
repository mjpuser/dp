import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Typography } from "@material-ui/core";
import Grid from "@material-ui/core/Grid";

export default function Pipelines({ datasets }) {
  return (
    <Grid container>
      <Grid item xs={12}>
        <Typography variant="h6">Datasets</Typography>
      </Grid>
      <Grid item xs={12}>
        <List>
          {datasets.map((d, i) => (
            <ListItem key={d.name} divider={i < pipelines.length - 1}>
              <ListItemText primary={d.name} />
            </ListItem>
          ))}
        </List>
      </Grid>
    </Grid>
  );
}

export async function getServerSideProps(context) {
  const res = await fetch("http://rest:3000/dataset");
  const data = await res.json();

  return {
    props: {
      datasets: data,
    },
  };
}
