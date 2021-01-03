import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import { Button, Typography } from "@material-ui/core";
import Icon from "@material-ui/core/Icon";
import Grid from "@material-ui/core/Grid";

export default function Pipelines({ pipelines }) {
  return (
    <Grid container>
      <Grid item xs={12}>
        <Typography variant="h6">Pipelines</Typography>
      </Grid>
      <Grid item xs={12}>
        <Button variant="contained" color="primary" href="/pipeline/new" endIcon={<Icon>add</Icon>}>
          Add
        </Button>
      </Grid>
      <Grid item xs={12}>
        <List>
          {pipelines.map((p) => (
            <ListItem key={p.id}>
              <ListItemText primary={p.name} />
            </ListItem>
          ))}
        </List>
      </Grid>
    </Grid>
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
